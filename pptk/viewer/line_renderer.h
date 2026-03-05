#ifndef __LINE_RENDERER_H__
#define __LINE_RENDERER_H__
#include <QOpenGLContext>
#include <QOpenGLShaderProgram>
#include <QWindow>
#include <vector>
#include "opengl_funcs.h"
#include "qt_camera.h"

class LineRenderer : protected OpenGLFuncs {
 public:
  LineRenderer(QWindow* window, QOpenGLContext* context)
      : _context(context),
        _window(window),
        _buffer_vertices(0),
        _buffer_colors(0),
        _buffer_indices(0),
        _num_indices(0),
        _line_width(1.0f) {
    _context->makeCurrent(_window);
    initializeOpenGLFunctions();
    _context->doneCurrent();
    compileProgram();
  }

  ~LineRenderer() { clear(); }

  void loadLines(const std::vector<float>& vertices,
                 const std::vector<unsigned int>& edges,
                 const std::vector<float>& colors,
                 float width) {
    clear();
    if (vertices.empty() || edges.empty()) return;
    _line_width = width;
    _num_indices = edges.size();
    _context->makeCurrent(_window);
    glGenBuffers(1, &_buffer_vertices);
    glBindBuffer(GL_ARRAY_BUFFER, _buffer_vertices);
    glBufferData(GL_ARRAY_BUFFER, sizeof(float) * vertices.size(),
                 (GLvoid*)&vertices[0], GL_STATIC_DRAW);
    glGenBuffers(1, &_buffer_colors);
    glBindBuffer(GL_ARRAY_BUFFER, _buffer_colors);
    if (colors.empty()) {
      std::vector<float> white(vertices.size() / 3 * 4, 1.0f);
      glBufferData(GL_ARRAY_BUFFER, sizeof(float) * white.size(),
                   (GLvoid*)&white[0], GL_STATIC_DRAW);
    } else {
      glBufferData(GL_ARRAY_BUFFER, sizeof(float) * colors.size(),
                   (GLvoid*)&colors[0], GL_STATIC_DRAW);
    }
    glGenBuffers(1, &_buffer_indices);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, _buffer_indices);
    glBufferData(GL_ELEMENT_ARRAY_BUFFER,
                 sizeof(unsigned int) * edges.size(),
                 (GLvoid*)&edges[0], GL_STATIC_DRAW);
    _context->doneCurrent();
  }

  void clear() {
    if (_num_indices == 0) return;
    _context->makeCurrent(_window);
    glDeleteBuffers(1, &_buffer_vertices);
    glDeleteBuffers(1, &_buffer_colors);
    glDeleteBuffers(1, &_buffer_indices);
    _context->doneCurrent();
    _num_indices = 0;
  }

  void draw(const QtCamera& camera, const vltools::Box3<float>& box) {
    if (_num_indices == 0) return;
    _program.bind();
    _program.setUniformValue("mvpMatrix", camera.computeMVPMatrix(box));
    glLineWidth(_line_width);
    _program.enableAttributeArray("position");
    _program.enableAttributeArray("color");
    glBindBuffer(GL_ARRAY_BUFFER, _buffer_vertices);
    _program.setAttributeArray("position", GL_FLOAT, 0, 3);
    glBindBuffer(GL_ARRAY_BUFFER, _buffer_colors);
    _program.setAttributeArray("color", GL_FLOAT, 0, 4);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, _buffer_indices);
    glDrawElements(GL_LINES, _num_indices, GL_UNSIGNED_INT, 0);
    _program.disableAttributeArray("position");
    _program.disableAttributeArray("color");
  }

  bool hasLines() const { return _num_indices > 0; }

 private:
  void compileProgram() {
    std::string vsCode =
        "#version 120\n"
        "uniform mat4 mvpMatrix;\n"
        "attribute vec3 position;\n"
        "attribute vec4 color;\n"
        "varying vec4 frag_color;\n"
        "void main() {\n"
        "  gl_Position = mvpMatrix * vec4(position, 1.0);\n"
        "  frag_color = color;\n"
        "}\n";
    std::string fsCode =
        "#version 120\n"
        "varying vec4 frag_color;\n"
        "void main() {\n"
        "  gl_FragColor = frag_color;\n"
        "}\n";
    _context->makeCurrent(_window);
    _program.addShaderFromSourceCode(QOpenGLShader::Vertex, vsCode.c_str());
    _program.addShaderFromSourceCode(QOpenGLShader::Fragment, fsCode.c_str());
    _program.link();
    _context->doneCurrent();
  }

  QOpenGLContext* _context;
  QWindow* _window;
  QOpenGLShaderProgram _program;
  GLuint _buffer_vertices;
  GLuint _buffer_colors;
  GLuint _buffer_indices;
  std::size_t _num_indices;
  float _line_width;
};

#endif  // __LINE_RENDERER_H__
