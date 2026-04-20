from manim import *
import numpy as np

bloch_scale = 0.7  # shrink vector (0.5–0.8 good range)

class BlochSphereRabi(ThreeDScene):

    def construct(self):

        # =========================
        # CAMERA (SLOWER ROTATION)
        # =========================
        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES, zoom=1.0)
        self.camera.background_color = "#0f0f12"

        # MUCH slower rotation
        self.begin_ambient_camera_rotation(rate=0.02)

        # =========================
        # GEOMETRY (LARGER SPHERE)
        # =========================
        R = 1.25  # <-- IMPORTANT FIX

        axes = ThreeDAxes(
            x_range=[-R, R, 1],
            y_range=[-R, R, 1],
            z_range=[-R, R, 1],
            x_length=4,
            y_length=4,
            z_length=4,
        )

        sphere = Sphere(radius=R, resolution=(12, 24))
        sphere.set_fill(BLUE_E, opacity=0.12)
        sphere.set_stroke(BLUE_D, opacity=0.3, width=1.2)

        # =========================
        # LABELS (UNCHANGED)
        # =========================
        label_offset = 1.4  # increase spacing (try 1.3–1.6)

        ket0 = Text("|0>").scale(0.7).move_to(axes.c2p(0, 0, label_offset))
        ket1 = Text("|1>").scale(0.7).move_to(axes.c2p(0, 0, -label_offset))

        ket_plus = Text("|+>").scale(0.7).move_to(axes.c2p(0, label_offset, 0))
        ket_minus = Text("|->").scale(0.7).move_to(axes.c2p(0, -label_offset, 0))

        ket_ip = Text("|+i>").scale(0.7).move_to(axes.c2p(label_offset, 0, 0))
        ket_im = Text("|-i>").scale(0.7).move_to(axes.c2p(-label_offset, 0, 0))
        labels = VGroup(ket0, ket1, ket_plus, ket_minus, ket_ip, ket_im)

        for l in labels:
            l.rotate(PI/2, axis=RIGHT)

        # =========================
        # PHYSICS
        # =========================

        Omega = 2 * np.pi * 1.0
        Delta = 2 * np.pi * 0.3

        rho = np.array([1+0j, 0+0j], dtype=complex)

        dt = 0.02

        speed_factor = 0.15  # <-- slower internal evolution
        step_counter = 0

        # =========================
        # BLOCH STEP
        # =========================

        def step(rho):

            a, b = rho

            rho_gg = np.abs(a)**2
            rho_ee = np.abs(b)**2
            rho_ge = a * np.conj(b)

            x = 2 * np.real(rho_ge)
            y = 2 * np.imag(rho_ge)
            z = rho_gg - rho_ee

            # FORCE ON SPHERE SURFACE
            r = np.sqrt(x*x + y*y + z*z)
            if r > 1e-12:
                x, y, z = R * x/r, R * y/r, R * z/r

            # Schrödinger evolution
            da = -1j * (Delta/2) * a - 1j * (Omega/2) * b
            db = +1j * (Delta/2) * b - 1j * (Omega/2) * a

            a_new = a + da * dt
            b_new = b + db * dt

            norm = np.sqrt(np.abs(a_new)**2 + np.abs(b_new)**2)
            a_new /= norm
            b_new /= norm

            return np.array([a_new, b_new]), x, y, z

        # =========================
        # BLOCH POSITION
        # =========================

        def bloch_point(x, y, z):
            return axes.c2p(bloch_scale * x, bloch_scale * y, bloch_scale * z)


        vec = Line(
            axes.c2p(0, 0, 0),
            axes.c2p(0, 0, bloch_scale),
            color=YELLOW,
            stroke_width=6
        )

        state = {"rho": rho}
        step_counter = 0

        # =========================
        # CLEAN UPDATER (NO GHOST DOTS)
        # =========================

        def update_vec(mob):
            nonlocal step_counter
            step_counter += 1

            if step_counter % int(1/speed_factor) != 0:
                return

            rho, x, y, z = step(state["rho"])
            state["rho"] = rho

            end = bloch_point(x, y, z)

            mob.put_start_and_end_on(axes.c2p(0, 0, 0), end)


        vec.add_updater(update_vec)


        # =========================
        # BUILD SCENE
        # =========================

        self.add(axes, sphere, labels)
        self.add(vec)


        self.wait(2)