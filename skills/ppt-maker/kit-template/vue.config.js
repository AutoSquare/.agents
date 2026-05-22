const path = require('path')
const webpack = require('webpack')
const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  // 不转译 pptxgenjs（避免 Babel 破坏其 import JSZip，且防止与 bundle 混编进同一 chunk）
  transpileDependencies: [],
  configureWebpack: {
    resolve: {
      alias: {
        pptxgenjs: path.resolve(__dirname, 'node_modules/pptxgenjs/dist/pptxgen.es.js'),
        // 避免 jszip package.json browser 字段指向 UMD 包
        jszip: path.resolve(__dirname, 'node_modules/jszip/lib/index.js'),
        'node:fs': false,
        'node:https': false,
      },
      fallback: {
        fs: false,
        https: false,
        http: false,
        path: false,
        stream: false,
        crypto: false,
      },
    },
    plugins: [
      new webpack.NormalModuleReplacementPlugin(/^node:/, (resource) => {
        resource.request = resource.request.replace(/^node:/, '')
      }),
      // bundle 依赖全局 JSZip，在 Webpack 中必然报错；一律改指向 es 构建
      new webpack.NormalModuleReplacementPlugin(
        /pptxgen\.bundle\.js$/,
        path.resolve(__dirname, 'node_modules/pptxgenjs/dist/pptxgen.es.js'),
      ),
      new webpack.ProvidePlugin({
        JSZip: path.resolve(__dirname, 'node_modules/jszip/lib/index.js'),
      }),
    ],
  },
})
