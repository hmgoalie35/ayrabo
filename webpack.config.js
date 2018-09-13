const path = require('path');
const webpack = require('webpack');
const glob = require('glob');

const ExtractTextPlugin = require('extract-text-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const BundleTracker = require('webpack-bundle-tracker');

// Paths
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
    vendor: path.join(jsxRoot, 'vendor.jsx'),
  },
  scss: {
    main: path.join(scssRoot, 'main.scss'),
  },
  dist: path.join(staticRoot, 'dist')
};

const generateEntryPoints = () => {
  const retVal = {
    jqueryMain: PATHS.js.main,
    // styleMain.js is never used
    styleMain: PATHS.scss.main,
    polyfills: ['babel-polyfill', 'raf/polyfill'],
    vendor: PATHS.jsx.vendor,
  };
  const entryPoints = glob.sync(path.join(jsxRoot, '**/entry.jsx'));
  entryPoints.map((entry) => {
    const entryName = path.basename(path.dirname(entry));
    retVal[entryName] = entry;
  });
  return retVal;
};

module.exports = function (env, argv) {
  const productionBuild = env.nodeEnv === 'production';

  let cssFileName = '[name]';
  let jsFileName = '[name]';
  if (productionBuild) {
    cssFileName = '[name].[contenthash]';
    jsFileName = '[name].[chunkhash]';
  }

  const extractScss = new ExtractTextPlugin(`css/${cssFileName}.css`);
  const entryPoints = generateEntryPoints();

  return {
    entry: entryPoints,
    output: {
      filename: `js/${jsFileName}.js`,
      path: PATHS.dist,
      pathinfo: !productionBuild,
      library: 'App',
      publicPath: '/static/dist/'
    },
    resolve: {
      extensions: ['.js', '.jsx', '.json']
    },
    stats: {
      // Don't show CopyWebpackPlugin output
      excludeAssets: [/^vendor/]
    },
    module: {
      rules: [
        {
          test: /\.jsx$/,
          include: [jsxRoot],
          use: [
            'babel-loader',
            {
              loader: 'eslint-loader',
              options: {
                cache: false,
              }
            }
          ],
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
    devtool: productionBuild ? '' : 'cheap-module-source-map',
    plugins: [
      new webpack.DefinePlugin({
        'process.env.NODE_ENV': JSON.stringify(env.nodeEnv)
      }),
      new CleanWebpackPlugin([PATHS.dist]),
      extractScss,
      new BundleTracker({ filename: './webpack-stats.json' }),
      new webpack.HashedModuleIdsPlugin(),
      // Anything shared b/w the vendor file and actual feature code will be moved to the vendor
      // chunk. Ex: react, react-dom, etc. The order here matters. After moving shared code  to the
      // vendor chunk, any other shared code will be moved to the commons chunk. Right now commons
      // should just contain the webpack boilerplate. Eventually other duplicated code not in the
      // vendor file will get moved there (because that's what happens when a chunk name isn't the
      // same as an entry point). I think adding another name called manifest should move the
      // webpack boilerplate to that chunk and leave duplicated code in commons.
      new webpack.optimize.CommonsChunkPlugin({
        names: ['vendor', 'commons'],
        minChunks: 2
      }),
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
