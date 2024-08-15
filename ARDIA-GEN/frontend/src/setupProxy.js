const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    '/api',
    createProxyMiddleware({
      //target: 'http://172.17.0.2:5000',
      target: 'http://backend:5000',
      //target: 'http://localhost:5000',
      //target: 'http://127.0.0.1:5000',
      //target: 'http://172.17.0.1:5000',
      changeOrigin: true,
      headers: {
          "Connection": "keep-alive"
      },

      // strip off the /api when passing through to the development server
      pathRewrite: {'^/api/' : '/'}
    })
  );
};