import time
import sys
import ctypes
from effects import BaseEffect

try:
    from OpenGL.GL import *
    from OpenGL.GL import shaders
    HAS_OPENGL = True
except ImportError:
    HAS_OPENGL = False
    print("PyOpenGL not found. Shader effects will be disabled.")

class ShaderEffect(BaseEffect):
    def __init__(self):
        super().__init__()
        self.program = None
        self.vao = None
        self.vbo = None
        self.start_time = time.time()
        self.resolution = (1920, 1080)
        self.initialized = False
        
    def get_vertex_shader(self):
        return """
        #version 330
        layout(location = 0) in vec2 position;
        out vec2 uv;
        void main() {
            uv = position * 0.5 + 0.5;
            gl_Position = vec4(position, 0.0, 1.0);
        }
        """

    def get_fragment_shader(self):
        # Default placeholder purple screen
        return """
        #version 330
        out vec4 fragColor;
        uniform float iTime;
        uniform vec2 iResolution;
        void main() {
            vec2 uv = gl_FragCoord.xy / iResolution.xy;
            fragColor = vec4(uv.x, uv.y, 0.5 + 0.5*sin(iTime), 1.0);
        }
        """

    def _compile_shaders(self):
        if not HAS_OPENGL: return False

        try:
            vertex_code = self.get_vertex_shader()
            fragment_code = self.get_fragment_shader()

            vertex = shaders.compileShader(vertex_code, GL_VERTEX_SHADER)
            fragment = shaders.compileShader(fragment_code, GL_FRAGMENT_SHADER)
            self.program = shaders.compileProgram(vertex, fragment)
            
            return True
        except Exception as e:
            print(f"Shader compilation failed for {self.__class__.__name__}:\n{e}")
            self.program = None
            return False

    def _init_gl(self):
        if not HAS_OPENGL: return
        if self.initialized: return

        if self._compile_shaders():
            # Full screen quad (x, y)
            # Triangle Strip: (-1,-1), (1,-1), (-1,1), (1,1)
            quad = [-1.0, -1.0,  1.0, -1.0,  -1.0, 1.0,  1.0, 1.0]
            quad_data = (ctypes.c_float * len(quad))(*quad)
            
            try:
                self.vao = glGenVertexArrays(1)
                glBindVertexArray(self.vao)
                
                self.vbo = glGenBuffers(1)
                glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
                glBufferData(GL_ARRAY_BUFFER, len(quad)*4, quad_data, GL_STATIC_DRAW)
                
                # Attribute 0: position
                loc = glGetAttribLocation(self.program, "position")
                if loc != -1:
                    glVertexAttribPointer(loc, 2, GL_FLOAT, GL_FALSE, 0, None)
                    glEnableVertexAttribArray(loc)
                
                glBindBuffer(GL_ARRAY_BUFFER, 0)
                glBindVertexArray(0)
                
                self.initialized = True
                
                # Debug GPU
                renderer = glGetString(GL_RENDERER)
                if renderer: renderer = renderer.decode('utf-8')
                vendor = glGetString(GL_VENDOR)
                if vendor: vendor = vendor.decode('utf-8')
                print(f"ShaderEffect {self.__class__.__name__} Initialized on: {renderer} ({vendor})")
            except Exception as e:
                print(f"GL Init Error: {e}")

    def draw(self, painter, w, h, phase):
        if not HAS_OPENGL: return

        # Sync resolution
        self.resolution = (w, h)
        
        # Prepare for raw GL
        painter.beginNativePainting()
        
        if not self.initialized:
            self._init_gl()
            
        if self.program and self.initialized:
            try:
                glUseProgram(self.program)
                
                # Uniforms
                elapsed = time.time() - self.start_time
                
                loc = glGetUniformLocation(self.program, "iTime")
                if loc != -1: glUniform1f(loc, elapsed)
                
                loc = glGetUniformLocation(self.program, "iResolution")
                if loc != -1: glUniform2f(loc, float(w), float(h))
                
                loc = glGetUniformLocation(self.program, "iAudio")
                if loc != -1:
                    bass = 0.0
                    mid = 0.0
                    treble = 0.0
                    if self.audio_data:
                        # Normalize audio? Already 0-1
                        bass = self.audio_data.get('bass', 0.0)
                        mid = self.audio_data.get('mid', 0.0)
                        treble = self.audio_data.get('treble', 0.0)
                    glUniform3f(loc, bass, mid, treble)

                # Draw
                glBindVertexArray(self.vao)
                glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
                glBindVertexArray(0)
                
                glUseProgram(0)
            except Exception as e:
                print(f"GL Draw Error: {e}")
                # Disable to avoid spam
                self.initialized = False
            
        painter.endNativePainting()
