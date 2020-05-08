import moderngl_window as mglw

__all__ = ['Example']


class Example(mglw.WindowConfig):
    gl_version = (3, 3)
    title = "Example"
    window_size = (1280, 720)
    aspect_ratio = 16 / 9
    resizable = True
    samples = 4

    @classmethod
    def run(cls):
        mglw.run_window_config(cls)
