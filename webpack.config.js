const path = require('path');
const glob = require('glob');

const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const BundleTracker = require('webpack-bundle-tracker');
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');


// Paths
const projectDir = path.resolve(__dirname);
const staticDir = path.join(projectDir, 'static');
const jsDir = path.join(staticDir, 'js');
const entryPointsDir = path.join(jsDir, 'entryPoints');
const scssDir = path.join(staticDir, 'scss');
const buildDir = path.join(staticDir, 'build');
const djangoStaticUrl = '/static/';
const publicPath = `${djangoStaticUrl}${path.basename(buildDir)}/`;

const generateEntryPoints = () => {
  const entryPoints = {};
  const rawEntryPoints = glob.sync(`${entryPointsDir}/*`);
  rawEntryPoints.map(entryPoint => {
    const fileName = path.basename(entryPoint, '.js');
    entryPoints[fileName] = entryPoint;
  });
  return entryPoints;
};

module.exports = function (env, argv) {
  const { mode } = argv;
  const isProduction = mode === 'production';
  const fileName = isProduction ? '[name].[contenthash]' : '[name]';
  const entry = generateEntryPoints();

  return {
    mode,
    entry,
    output: {
      filename: `js/${fileName}.js`,
      chunkFilename: `js/${fileName}.js`,
      path: buildDir,
      library: 'App',
      publicPath,
    },
    stats: {
      // Don't show CopyWebpackPlugin output
      excludeAssets: [/^vendor/]
    },
    optimization: {
      runtimeChunk: 'single',
      moduleIds: 'hashed',
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
    },
    module: {
      rules: [
        {
          test: /\.js$/,
          include: [jsDir],
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
          include: [scssDir],
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
                sassOptions: {
                  precision: 8
                }
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
    watch: !isProduction,
    plugins: [
      // new BundleAnalyzerPlugin(),
      new CleanWebpackPlugin(),
      new MiniCssExtractPlugin({
        filename: `css/${fileName}.css`
      }),
      new BundleTracker({ filename: './webpack-stats.json' }),
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
