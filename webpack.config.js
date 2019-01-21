const path = require('path');
const webpack = require('webpack');
const glob = require('glob');

const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const BundleTracker = require('webpack-bundle-tracker');
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;


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
    main: path.join(jsxRoot, 'main.jsx'),
    vendor: path.join(jsxRoot, 'vendor.jsx')
  },
  dist: path.join(staticRoot, 'dist')
};

const generateEntryPoints = () => {
  const retVal = {
    jqueryMain: PATHS.js.main,
    main: PATHS.jsx.main,
    vendor: PATHS.jsx.vendor,
    polyfills: ['babel-polyfill', 'raf/polyfill'],
  };
  const entryPoints = glob.sync(path.join(jsxRoot, '**/entry.jsx'));
  entryPoints.map((entry) => {
    const entryName = path.basename(path.dirname(entry));
    retVal[entryName] = entry;
  });
  return retVal;
};

module.exports = function (env, argv) {
  // PyCharm's webpack feature wasn't working because `argv` was undefined.
  const mode = argv ? argv.mode : 'development';
  const productionBuild = mode === 'production';

  let cssFileName = '[name]';
  let jsFileName = '[name]';
  if (productionBuild) {
    cssFileName = '[name].[contenthash]';
    jsFileName = '[name].[contenthash]';
  }

  const entryPoints = generateEntryPoints();

  return {
    entry: entryPoints,
    output: {
      filename: `js/${jsFileName}.js`,
      chunkFilename: `js/${jsFileName}.js`,
      path: PATHS.dist,
      library: 'App',
      publicPath: '/static/dist/'
    },
    resolve: {
      extensions: ['.js', '.jsx', '.json'],
      symlinks: false
    },
    stats: {
      // Don't show CopyWebpackPlugin output
      excludeAssets: [/^vendor/]
    },
    optimization: {
      splitChunks: {
        cacheGroups: {
          globals: {
            name: 'globals',
            chunks: 'all',
            test: /(noty\.js|clipboard)/,
            minChunks: 1
          }
        }
      },
      runtimeChunk: 'single'
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
          use: [
            MiniCssExtractPlugin.loader,
            {
              loader: 'css-loader',
              options: {
                importLoaders: 2,
              }
            },
            {
              loader: 'postcss-loader',
              options: {
                ident: 'postcss',
                plugins: [
                  require('autoprefixer')
                ]
              }
            },
            {
              loader: 'sass-loader',
              options: {
                precision: 8
              }
            }
          ]
        },
        {
          test: /\.(png|svg|jpe?g|gif)(\?v=\d+\.\d+\.\d+)?$/,
          loader: 'file-loader',
          options: {
            outputPath: 'img/'
          }
        },
        {
          test: /\.(woff|woff2|eot|ttf|otf)(\?v=\d+\.\d+\.\d+)?$/,
          loader: 'file-loader',
          options: {
            outputPath: 'fonts/'
          }
        },
        {
          test: require.resolve('noty'),
          use: [
            {
              loader: 'expose-loader',
              options: 'Noty'
            }
          ]
        },
        {
          test: require.resolve('clipboard'),
          use: [
            {
              loader: 'expose-loader',
              options: 'ClipboardJS'
            }
          ]
        }
      ],
    },
    devtool: productionBuild ? '' : 'cheap-module-source-map',
    plugins: [
      // new BundleAnalyzerPlugin(),
      new CleanWebpackPlugin([PATHS.dist]),
      new MiniCssExtractPlugin({
        filename: `css/${cssFileName}.css`
      }),
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
