var gulp = require('gulp');
var shell = require('gulp-shell');
var connect = require('gulp-connect');

gulp.task('build-docs', shell.task('sphinx-build docs docs/build/html'));

gulp.task('docs', ['build-docs'], function() {
  gulp.watch(['./docs/*.rst', './docs/*.py'], ['build-docs']);
});

gulp.task('connect', function() {
  connect.server({
    root: 'docs/build/html',
    livereload: true
  });
});

// gulp.task('watch', function () {
//   gulp.watch(['./app/*.html'], ['docs']);
// });

gulp.task('default', ['connect', 'docs']);
