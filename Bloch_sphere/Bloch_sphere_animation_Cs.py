from manim import *
import numpy as np

#run "manim -pql Bloch_sphere_animation_Cs.py Cs_Bloch_sphere_anaimation --fps 60"

bloch_scale = 0.5

class BlochSphereRabi(ThreeDScene):

    def construct(self):

        # =========================
        # CAMERA
        # =========================
        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES, zoom=1.0)
        self.camera.background_color = "#0f0f12"
        self.begin_ambient_camera_rotation(rate=0.02)

        # =========================
        # GEOMETRY
        # =========================
        R = 1

        axes = ThreeDAxes(
            x_range=[-R, R, 1],
            y_range=[-R, R, 1],
            z_range=[-R, R, 1],
            x_length=4,
            y_length=4,
            z_length=4,
            axis_config={"include_tip": False}
        )

        sphere = Sphere(radius=R, resolution=(12, 24))
        sphere.set_fill(BLUE_E, opacity=0.12)
        sphere.set_stroke(BLUE_D, opacity=0.3, width=1.2)

        # =========================
        # LABELS
        # =========================
        label_offset = 1.4

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
        # PHYSICS (stronger motion)
        # =========================
        Omega = 2 * np.pi * 3.0   # increased drive
        Delta = 2 * np.pi * 1.0   # increased detuning

        rho = np.array([1+0j, 0+0j], dtype=complex)

        dt = 0.005
        speed_factor = 0.15
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

            # NO projection to sphere → allows richer motion
            x, y, z = R * x, R * y, R * z

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
        # VECTOR POSITION
        # =========================
        def bloch_point(x, y, z):
            return axes.c2p(bloch_scale * x, bloch_scale * y, bloch_scale * z)

        # =========================
        # TRUE 3D ARROW VECTOR
        # =========================
        vec = Arrow3D(
            start=axes.c2p(0, 0, 0),
            end=axes.c2p(0, 0, bloch_scale),
            color=YELLOW,
        )

        state = {"rho": rho}
        step_counter = 0

        # =========================
        # UPDATER
        # =========================
        def update_vec(mob):
            nonlocal step_counter
            step_counter += 1

            if step_counter % int(1/speed_factor) != 0:
                return

            rho, x, y, z = step(state["rho"])
            state["rho"] = rho

            end = bloch_point(x, y, z)

            new_vec = Arrow3D(
                start=axes.c2p(0, 0, 0),
                end=end,
                color=YELLOW,
            )

            mob.become(new_vec)

        vec.add_updater(update_vec)

        # =========================
        # SCENE
        # =========================
        self.add(axes, sphere, labels)
        self.add(vec)

        self.wait(10)