"""
=============================================================
  GENERAL PURPOSE 2D PHYSICS SIMULATION ENGINE
  - Particles + Forces + Integrators
  - Runs continuously until your stopping condition is met
=============================================================
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from typing import List, Callable, Optional, Dict, Any
import time


class Particle:
    """Single particle with mass, position, velocity, and optional radius/charge"""
    
    def __init__(self, 
                 mass: float = 1.0, 
                 pos: np.ndarray = None, 
                 vel: np.ndarray = None,
                 radius: float = 0.1,
                 charge: float = 0.0,
                 color: str = 'blue',
                 name: str = ""):
        
        self.mass = float(mass)
        self.pos = np.array(pos if pos is not None else [0.0, 0.0], dtype=float)
        self.vel = np.array(vel if vel is not None else [0.0, 0.0], dtype=float)
        self.force = np.zeros(2, dtype=float)   # Accumulated force this step
        self.radius = float(radius)
        self.charge = float(charge)
        self.color = color
        self.name = name
        self.trail = [self.pos.copy()]          # For path visualization
        
    def reset_force(self):
        self.force[:] = 0.0
        
    def apply_force(self, f: np.ndarray):
        self.force += f
        
    def kinetic_energy(self) -> float:
        return 0.5 * self.mass * np.dot(self.vel, self.vel)
    
    def __repr__(self):
        return f"Particle({self.name or 'unnamed'}, m={self.mass:.2f}, pos={self.pos})"


class Force:
    """Base class for forces. Override calculate()"""
    
    def calculate(self, particles: List[Particle], t: float = 0.0) -> None:
        """Apply forces to particles (modifies particle.force in-place)"""
        raise NotImplementedError


class Gravity(Force):
    """Uniform gravity (downward by default)"""
    
    def __init__(self, g: float = 9.81, direction: np.ndarray = None):
        self.g = g
        self.direction = np.array(direction if direction is not None else [0.0, -1.0], dtype=float)
        self.direction /= np.linalg.norm(self.direction)
        
    def calculate(self, particles: List[Particle], t: float = 0.0):
        for p in particles:
            p.apply_force(p.mass * self.g * self.direction)


class Spring(Force):
    """Hooke's law spring between two particles (or particle and fixed point)"""
    
    def __init__(self, p1_idx: int, p2_idx: Optional[int], 
                 k: float = 10.0, rest_length: float = 1.0,
                 fixed_point: np.ndarray = None, damping: float = 0.0):
        self.p1 = p1_idx
        self.p2 = p2_idx
        self.k = k
        self.rest_length = rest_length
        self.fixed_point = np.array(fixed_point, dtype=float) if fixed_point is not None else None
        self.damping = damping
        
    def calculate(self, particles: List[Particle], t: float = 0.0):
        p1 = particles[self.p1]
        
        if self.p2 is not None:
            p2 = particles[self.p2]
            delta = p2.pos - p1.pos
            rel_vel = p2.vel - p1.vel
        else:
            delta = self.fixed_point - p1.pos
            rel_vel = -p1.vel
            
        dist = np.linalg.norm(delta)
        if dist < 1e-8:
            return
            
        direction = delta / dist
        spring_force = self.k * (dist - self.rest_length) * direction
        damping_force = self.damping * np.dot(rel_vel, direction) * direction
        
        force = spring_force + damping_force
        
        p1.apply_force(force)
        if self.p2 is not None:
            p2.apply_force(-force)


class Drag(Force):
    """Linear + quadratic air resistance"""
    
    def __init__(self, linear: float = 0.1, quadratic: float = 0.0):
        self.linear = linear
        self.quadratic = quadratic
        
    def calculate(self, particles: List[Particle], t: float = 0.0):
        for p in particles:
            speed = np.linalg.norm(p.vel)
            if speed > 1e-8:
                drag = -self.linear * p.vel - self.quadratic * speed * p.vel
                p.apply_force(drag)


class PairwiseGravity(Force):
    """Newtonian gravity between all particles (G is softened for stability)"""
    
    def __init__(self, G: float = 1.0, softening: float = 0.1):
        self.G = G
        self.softening = softening
        
    def calculate(self, particles: List[Particle], t: float = 0.0):
        n = len(particles)
        for i in range(n):
            for j in range(i + 1, n):
                delta = particles[j].pos - particles[i].pos
                dist2 = np.dot(delta, delta) + self.softening**2
                dist = np.sqrt(dist2)
                force_mag = self.G * particles[i].mass * particles[j].mass / dist2
                force = force_mag * delta / dist
                
                particles[i].apply_force(force)
                particles[j].apply_force(-force)


class CustomForce(Force):
    """User-defined force via a function: fn(particles, t) -> None"""
    
    def __init__(self, fn: Callable[[List[Particle], float], None]):
        self.fn = fn
        
    def calculate(self, particles: List[Particle], t: float = 0.0):
        self.fn(particles, t)


class Simulation:
    """
    Main simulation engine.
    
    Usage:
        sim = Simulation(particles, forces)
        sim.run_until(stop_condition, dt=0.01, max_steps=100000)
    """
    
    def __init__(self, 
                 particles: List[Particle], 
                 forces: List[Force] = None,
                 integrator: str = "verlet"):
        
        self.particles = particles
        self.forces = forces if forces is not None else []
        self.integrator = integrator.lower()
        self.time = 0.0
        self.step_count = 0
        self.history = []          # Optional: store states
        
        valid = ["euler", "verlet", "rk4"]
        if self.integrator not in valid:
            raise ValueError(f"Integrator must be one of {valid}")
    
    def _compute_forces(self):
        for p in self.particles:
            p.reset_force()
        for force in self.forces:
            force.calculate(self.particles, self.time)
    
    def _euler_step(self, dt: float):
        self._compute_forces()
        for p in self.particles:
            acc = p.force / p.mass
            p.pos += p.vel * dt
            p.vel += acc * dt
    
    def _verlet_step(self, dt: float):
        # Velocity Verlet (better energy conservation)
        self._compute_forces()
        for p in self.particles:
            acc = p.force / p.mass
            p.pos += p.vel * dt + 0.5 * acc * dt**2
            p.vel += 0.5 * acc * dt   # half step
        
        self._compute_forces()
        for p in self.particles:
            acc = p.force / p.mass
            p.vel += 0.5 * acc * dt   # complete the velocity update
    
    def _rk4_step(self, dt: float):
        # Classic 4th order Runge-Kutta
        n = len(self.particles)
        # Save initial state
        pos0 = np.array([p.pos.copy() for p in self.particles])
        vel0 = np.array([p.vel.copy() for p in self.particles])
        
        def get_acc():
            self._compute_forces()
            return np.array([p.force / p.mass for p in self.particles])
        
        # k1
        a1 = get_acc()
        k1_v = a1
        k1_x = vel0
        
        # k2
        for i, p in enumerate(self.particles):
            p.pos = pos0[i] + 0.5 * dt * k1_x[i]
            p.vel = vel0[i] + 0.5 * dt * k1_v[i]
        a2 = get_acc()
        k2_v = a2
        k2_x = vel0 + 0.5 * dt * k1_v
        
        # k3
        for i, p in enumerate(self.particles):
            p.pos = pos0[i] + 0.5 * dt * k2_x[i]
            p.vel = vel0[i] + 0.5 * dt * k2_v[i]
        a3 = get_acc()
        k3_v = a3
        k3_x = vel0 + 0.5 * dt * k2_v
        
        # k4
        for i, p in enumerate(self.particles):
            p.pos = pos0[i] + dt * k3_x[i]
            p.vel = vel0[i] + dt * k3_v[i]
        a4 = get_acc()
        k4_v = a4
        k4_x = vel0 + dt * k3_v
        
        # Final update
        for i, p in enumerate(self.particles):
            p.pos = pos0[i] + (dt / 6.0) * (k1_x[i] + 2*k2_x[i] + 2*k3_x[i] + k4_x[i])
            p.vel = vel0[i] + (dt / 6.0) * (k1_v[i] + 2*k2_v[i] + 2*k3_v[i] + k4_v[i])
    
    def step(self, dt: float):
        if self.integrator == "euler":
            self._euler_step(dt)
        elif self.integrator == "verlet":
            self._verlet_step(dt)
        elif self.integrator == "rk4":
            self._rk4_step(dt)
            
        self.time += dt
        self.step_count += 1
        
        # Optional trail update (keep last N points)
        for p in self.particles:
            p.trail.append(p.pos.copy())
            if len(p.trail) > 500:
                p.trail.pop(0)
    
    def run_until(self, 
                  stop_condition: Callable[["Simulation"], bool],
                  dt: float = 0.01,
                  max_steps: int = 100_000,
                  print_every: int = 1000,
                  store_history: bool = False) -> Dict[str, Any]:
        """
        Keep simulating until stop_condition(sim) returns True
        or max_steps is reached.
        
        Returns a dictionary with results.
        """
        print(f"▶ Simulation started | Integrator: {self.integrator} | dt={dt}")
        start_wall = time.time()
        
        while self.step_count < max_steps:
            self.step(dt)
            
            if store_history:
                state = {
                    "time": self.time,
                    "positions": [p.pos.copy() for p in self.particles],
                    "velocities": [p.vel.copy() for p in self.particles]
                }
                self.history.append(state)
            
            if self.step_count % print_every == 0:
                print(f"  Step {self.step_count:6d} | t = {self.time:8.3f}s")
            
            if stop_condition(self):
                break
        
        wall_time = time.time() - start_wall
        success = stop_condition(self)
        
        result = {
            "success": success,
            "final_time": self.time,
            "steps": self.step_count,
            "wall_time": wall_time,
            "particles": self.particles,
        }
        
        print("\n" + "="*50)
        if success:
            print(f"✅ Result found after {self.step_count} steps")
            print(f"   Simulation time : {self.time:.4f} s")
            print(f"   Wall clock time : {wall_time:.3f} s")
        else:
            print(f"⚠️  Max steps ({max_steps}) reached without meeting condition")
            print(f"   Final time: {self.time:.4f} s")
        print("="*50)
        
        return result
    
    def total_energy(self) -> float:
        """Rough kinetic energy (potential depends on forces)"""
        return sum(p.kinetic_energy() for p in self.particles)
    
    def plot(self, show_trails: bool = True, title: str = "Physics Simulation"):
        """Simple static plot of current positions + trails"""
        fig, ax = plt.subplots(figsize=(9, 7))
        
        for p in self.particles:
            if show_trails and len(p.trail) > 1:
                trail = np.array(p.trail)
                ax.plot(trail[:, 0], trail[:, 1], alpha=0.4, color=p.color, linewidth=1)
            
            circle = plt.Circle(p.pos, p.radius, color=p.color, zorder=5)
            ax.add_patch(circle)
            ax.plot(p.pos[0], p.pos[1], 'o', color=p.color, markersize=2)
            
            if p.name:
                ax.annotate(p.name, p.pos, textcoords="offset points", xytext=(5,5), fontsize=9)
        
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_title(title)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        plt.tight_layout()
        return fig, ax


# ============================================================
# READY-TO-RUN EXAMPLES
# ============================================================

def example_projectile_until_ground():
    """Projectile motion – run until it hits the ground (y <= 0)"""
    print("\n🚀 Example 1: Projectile Motion (until hits ground)\n")
    
    p = Particle(mass=1.0, pos=[0, 10], vel=[15, 25], radius=0.3, color='crimson', name="Ball")
    
    sim = Simulation([p], forces=[Gravity(g=9.81), Drag(linear=0.05)], integrator="verlet")
    
    def hit_ground(sim):
        return sim.particles[0].pos[1] <= 0.0
    
    result = sim.run_until(hit_ground, dt=0.005, max_steps=50000, print_every=500)
    
    print(f"\nLanding position : x = {result['particles'][0].pos[0]:.3f} m")
    print(f"Final velocity   : {result['particles'][0].vel}")
    
    fig, ax = sim.plot(title="Projectile Motion – until ground impact")
    ax.axhline(0, color='black', linewidth=2)
    plt.savefig("/home/workdir/artifacts/projectile.png", dpi=120)
    plt.close()
    print("Plot saved → projectile.png")
    return result


def example_spring_until_rest():
    """Spring-mass system – run until almost at rest"""
    print("\n🌀 Example 2: Damped Spring-Mass (until almost rest)\n")
    
    p = Particle(mass=1.0, pos=[1.5, 0], vel=[0, 0], radius=0.15, color='teal', name="Mass")
    
    spring = Spring(p1_idx=0, p2_idx=None, k=20.0, rest_length=1.0, 
                    fixed_point=[0, 0], damping=1.5)
    
    sim = Simulation([p], forces=[spring], integrator="verlet")
    
    def almost_rest(sim):
        speed = np.linalg.norm(sim.particles[0].vel)
        extension = abs(np.linalg.norm(sim.particles[0].pos) - 1.0)
        return speed < 0.01 and extension < 0.02
    
    result = sim.run_until(almost_rest, dt=0.01, max_steps=20000)
    
    fig, ax = sim.plot(title="Damped Spring → Equilibrium")
    ax.plot(0, 0, 'ks', markersize=10, label="Fixed point")
    ax.legend()
    plt.savefig("/home/workdir/artifacts/spring.png", dpi=120)
    plt.close()
    print("Plot saved → spring.png")
    return result


def example_orbit_until_period():
    """Two-body orbit – run for approximately one period"""
    print("\n🪐 Example 3: Simple 2-body Orbit\n")
    
    # Central body
    sun = Particle(mass=100.0, pos=[0, 0], vel=[0, 0], radius=0.4, color='orange', name="Sun")
    # Planet
    planet = Particle(mass=1.0, pos=[5, 0], vel=[0, 4.5], radius=0.2, color='royalblue', name="Planet")
    
    sim = Simulation([sun, planet], 
                     forces=[PairwiseGravity(G=1.0, softening=0.05)], 
                     integrator="verlet")
    
    # Stop after roughly one orbital period (we estimate)
    target_time = 8.0   # approximate
    
    def one_period(sim):
        return sim.time >= target_time
    
    result = sim.run_until(one_period, dt=0.005, max_steps=50000, print_every=1000)
    
    fig, ax = sim.plot(title="2-Body Gravitational Orbit")
    plt.savefig("/home/workdir/artifacts/orbit.png", dpi=120)
    plt.close()
    print("Plot saved → orbit.png")
    return result


if __name__ == "__main__":
    print("="*60)
    print("   GENERAL 2D PHYSICS SIMULATION ENGINE")
    print("   Runs until your condition is satisfied")
    print("="*60)
    
    # Run examples
    example_projectile_until_ground()
    example_spring_until_rest()
    example_orbit_until_period()
    
    print("\n✅ All examples completed successfully!")
    print("You can now import this engine and create your own simulations.")
              
