from manim import *
import numpy as np

class BlochSphere(ThreeDScene):
    def construct(self):
        # --- Camera ---
        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES, zoom=1.0)
        self.camera.background_color = "#0f0f12"

        # --- Axes ---
        axes = ThreeDAxes(
            x_range=[-1.2, 1.2, 1],
            y_range=[-1.2, 1.2, 1],
            z_range=[-1.2, 1.2, 1],
            x_length=6,
            y_length=6,
            z_length=6,
        )
        labels = VGroup(
            Text("X", font_size=28).move_to(axes.c2p(1.35, 0, 0)),
            Text("Y", font_size=28).move_to(axes.c2p(0, 1.35, 0)),
            Text("Z", font_size=28).move_to(axes.c2p(0, 0, 1.35)),
        )
        # Make labels face the camera
        for lab in labels:
            lab.rotate(PI/2, axis=RIGHT)

        # --- Sphere ---
        sphere = Sphere(radius=1, resolution=(24, 48))
        sphere.set_fill(BLUE_E, opacity=0.12)
        sphere.set_stroke(BLUE_D, opacity=0.35, width=1.5)

        # --- Great circles (equator + a couple meridians) ---
        equator = Circle(radius=1).set_stroke(WHITE, opacity=0.35, width=2)
        equator.rotate(PI/2, axis=RIGHT)  # Put in X-Y plane

        meridian_1 = Circle(radius=1).set_stroke(WHITE, opacity=0.25, width=2)
        meridian_1.rotate(PI/2, axis=UP)  # Put in Y-Z-ish

        meridian_2 = Circle(radius=1).set_stroke(WHITE, opacity=0.25, width=2)
        meridian_2.rotate(PI/2, axis=UP)
        meridian_2.rotate(PI/2, axis=OUT)  # rotate around Z to get another meridian

        # --- Poles labels |0>, |1> (optional) ---
        ket0 = MathTex(r"\left|0\right\rangle").scale(0.8).move_to(axes.c2p(0, 0, 1.25))
        ket1 = MathTex(r"\left|1\right\rangle").scale(0.8).move_to(axes.c2p(0, 0, -1.35))
        for m in (ket0, ket1):
            m.rotate(PI/2, axis=RIGHT)

        # --- Bloch vector as function of theta, phi ---
        theta = ValueTracker(35 * DEGREES)   # polar angle from +Z
        phi = ValueTracker(40 * DEGREES)     # azimuthal angle in X-Y plane

        def bloch_point():
            th = theta.get_value()
            ph = phi.get_value()
            x = np.sin(th) * np.cos(ph)
            y = np.sin(th) * np.sin(ph)
            z = np.cos(th)
            return axes.c2p(x, y, z)

        # Tip dot on sphere
        tip = always_redraw(
            lambda: Dot3D(point=bloch_point(), radius=0.06, color=YELLOW)
        )

        # Vector arrow from origin to tip
        vec = always_redraw(
            lambda: Arrow3D(
                start=axes.c2p(0, 0, 0),
                end=bloch_point(),
                color=YELLOW,
                thickness=0.02
            )
        )

        # Optional: draw the projection onto equatorial plane
        proj = always_redraw(
            lambda: DashedLine(
                start=bloch_point(),
                end=axes.c2p(
                    np.sin(theta.get_value()) * np.cos(phi.get_value()),
                    np.sin(theta.get_value()) * np.sin(phi.get_value()),
                    0
                ),
                dash_length=0.08
            ).set_stroke(YELLOW, opacity=0.6, width=2)
        )

        # Optional: show theta, phi values on screen (2D overlay)
        readout = always_redraw(
            lambda: VGroup(
                MathTex(r"\theta=", f"{theta.get_value()/DEGREES:.1f}^\\circ").scale(0.7),
                MathTex(r"\phi=", f"{phi.get_value()/DEGREES:.1f}^\\circ").scale(0.7),
            ).arrange(DOWN, aligned_edge=LEFT).to_corner(UL)
        )

        # --- Build scene ---
        self.add(axes, labels)
        self.add(sphere, equator, meridian_1, meridian_2, ket0, ket1)
        self.add(vec, tip, proj)
        self.add_fixed_in_frame_mobjects(readout)

        self.begin_ambient_camera_rotation(rate=0.12)

        # --- Animations ---
        self.play(theta.animate.set_value(75 * DEGREES), phi.animate.set_value(180 * DEGREES), run_time=3)
        self.play(theta.animate.set_value(20 * DEGREES), phi.animate.set_value(300 * DEGREES), run_time=3)
        self.play(theta.animate.set_value(110 * DEGREES), phi.animate.set_value(40 * DEGREES), run_time=3)

        self.wait(1)
