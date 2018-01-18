const path = require('path');
const webpack = require('webpack');

const ExtractTextPlugin = require('extract-text-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const BundleTracker = require('webpack-bundle-tracker');

const projectRoot = path.resolve(__dirname);
const staticRoot = path.join(projectRoot, 'static');
const jsRoot = path.join(staticRoot, 'js');
const jsxRoot = path.join(staticRoot, 'jsx');
const scssRoot = path.join(staticRoot, 'scss');

const PATHS = {
  js: {
    main: path.join(jsRoot, 'main.js'),
  },
  jsx: {
    main: path.join(jsxRoot, 'main.jsx'),
  },
  scss: {
    main: path.join(scssRoot, 'main.scss'),
  },
  dist: path.join(staticRoot, 'dist')
};

module.exports = function (env, argv) {
  const productionBuild = env.nodeEnv === 'production';

  let cssFileName = '[name]';
  let jsFileName = '[name]';
  if (productionBuild) {
    cssFileName = '[name].[chunkhash]';
    jsFileName = '[name].[chunkhash]';
  }

  const extractScss = new ExtractTextPlugin(`css/${cssFileName}.css`);

  return {
    entry: {
      jqueryMain: PATHS.js.main,
      reactMain: PATHS.jsx.main,
      // styleMain.js is never used
      styleMain: PATHS.scss.main,
      polyfills: ['babel-polyfill'],
    },
    output: {
      filename: `js/${jsFileName}.js`,
      path: PATHS.dist,
      library: 'App',
      publicPath: '/static/dist/'
    },
    module: {
      rules: [
        {
          test: /\.jsx$/,
          include: [jsxRoot],
          loader: 'babel-loader',
        },
        {
          test: /\.scss$/,
          include: [scssRoot],
          use: extractScss.extract({
            fallback: 'style-loader',
            use: [
              {
                loader: 'css-loader',
                options: {
                  importLoaders: 1
                }
              },
              'postcss-loader',
              {
                loader: 'sass-loader',
                options: {
                  precision: 8
                }
              }
            ]
          })
        },
        {
          test: /\.(png|svg|jpe?g|gif)$/,
          use: {
            loader: 'file-loader',
            options: {
              outputPath: 'img/'
            }
          }
        },
        {
          test: /\.(woff|woff2|eot|ttf|otf)(\?v=\d+\.\d+\.\d+)?$/,
          loader: 'file-loader',
          options: {
            outputPath: 'fonts/'
          }
        }
      ],
    },
    devtool: productionBuild ? '' : 'cheap-module-eval-source-map',
    plugins: [
      new webpack.DefinePlugin({
        'process.env.NODE_ENV': JSON.stringify(env.nodeEnv)
      }),
      new CleanWebpackPlugin([PATHS.dist]),
      extractScss,
      new BundleTracker({ filename: './webpack-stats.json' }),
      new webpack.HashedModuleIdsPlugin(),
      new CopyWebpackPlugin([
        {
          from: 'jquery/dist/jquery.min.js',
          to: 'vendor',
          context: 'node_modules'
        },
        {
          from: 'bootstrap-sass/assets/javascripts/bootstrap.min.js',
          to: 'vendor',
          context: 'node_modules'
        },
        {
          from: 'bootstrap-select/dist',
          to: 'vendor/bootstrap-select',
          context: 'node_modules'
        },
        {
          from: 'noty/lib/noty.min.js',
          to: 'vendor',
          context: 'node_modules'
        },
        {
          from: 'noty/lib/noty.css',
          to: 'vendor',
          context: 'node_modules'
        },
        {
          from: 'animate.css/animate.min.css',
          to: 'vendor',
          context: 'node_modules'
        },
        {
          from: 'font-awesome/css',
          to: 'vendor/font-awesome/css',
          context: 'node_modules'
        },
        {
          from: 'font-awesome/fonts',
          to: 'vendor/font-awesome/fonts',
          context: 'node_modules'
        },
        {
          from: 'eonasdan-bootstrap-datetimepicker/build/js',
          to: 'vendor/bootstrap-datetimepicker/js',
          context: 'node_modules'
        },
        {
          from: 'eonasdan-bootstrap-datetimepicker/build/css/bootstrap-datetimepicker.min.css',
          to: 'vendor/bootstrap-datetimepicker/css',
          context: 'node_modules'
        },
        {
          from: 'moment/min/moment.min.js',
          to: 'vendor',
          context: 'node_modules'
        },
        {
          from: 'moment/min/locales.min.js',
          to: 'vendor',
          context: 'node_modules'
        },
        {
          from: 'moment-timezone/builds/moment-timezone.min.js',
          to: 'vendor',
          context: 'node_modules'
        },
        {
          from: 'datatables.net/js',
          to: 'vendor/datatables',
          context: 'node_modules'
        },
        {
          from: 'datatables.net-bs/css',
          to: 'vendor/datatables',
          context: 'node_modules'
        },
        {
          from: 'datatables.net-bs/js',
          to: 'vendor/datatables',
          context: 'node_modules'
        }
      ])
    ]
  };
};
