const path = require('path');
const glob = require('glob');

const MiniCssExtractPlugin = require('mini-css-extract-plugin');
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
      library: '[name]',
      publicPath,
    },
    optimization: {
      runtimeChunk: 'single',
      moduleIds: isProduction ? 'hashed' : 'named',
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
          test: require.resolve('clipboard'),
          use: [
            {
              loader: 'expose-loader',
              options: 'ClipboardJS'
            }
          ]
        },
        {
          test: require.resolve('jquery'),
          use: [
            {
              loader: 'expose-loader',
              options: 'jQuery'
            },
            {
              loader: 'expose-loader',
              options: '$'
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
      new BundleTracker({ filename: './webpack-stats.json' })
    ]
  };
};
