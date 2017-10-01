const path = require('path');

const ExtractTextPlugin = require("extract-text-webpack-plugin");
const CopyWebpackPlugin = require("copy-webpack-plugin");
const CleanWebpackPlugin = require('clean-webpack-plugin');
const BundleTracker = require('webpack-bundle-tracker');

const extractScss = new ExtractTextPlugin("css/[name].css");

const projectRoot = path.resolve(__dirname);
const staticRoot = path.join(projectRoot, 'static');
const jsRoot = path.join(staticRoot, 'js');
const scssRoot = path.join(staticRoot, 'scss');


const PATHS = {
  js: {
    main: path.join(jsRoot, 'main.js'),
  },
  dist: path.join(staticRoot, 'dist')
};

module.exports = {
  entry: {
    main: PATHS.js.main
  },
  output: {
    filename: "js/[name].js",
    path: PATHS.dist,
    library: "App",
    publicPath: "/static/dist/"
  },
  module: {
    rules: [
      {
        test: /\.scss$/,
        include: [scssRoot],
        use: extractScss.extract({
          fallback: "style-loader",
          use: [
            {
              loader: "css-loader",
              options: {
                importLoaders: 1
              }
            },
            "postcss-loader",
            {
              loader: "sass-loader",
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
          loader: "file-loader",
          options: {
            outputPath: "img/"
          }
        }
      },
      {
        test: /\.(woff|woff2|eot|ttf|otf)$/,
        loader: "file-loader",
        options: {
          outputPath: "fonts/"
        }
      }
    ],
  },
  plugins: [
    new CleanWebpackPlugin([PATHS.dist]),
    extractScss,
    new BundleTracker({ filename: "./webpack-stats.json" }),
    new CopyWebpackPlugin([
      {
        from: "jquery/dist/jquery.min.js",
        to: "vendor",
        context: "node_modules"
      },
      {
        from: "bootstrap-sass/assets/javascripts/bootstrap.min.js",
        to: "vendor",
        context: "node_modules"
      },
      {
        from: "bootstrap-select/dist",
        to: "vendor/bootstrap-select",
        context: "node_modules"
      },
      {
        from: "noty/js/noty/packaged/jquery.noty.packaged.min.js",
        to: "vendor",
        context: "node_modules"
      },
      {
        from: "animate.css/animate.min.css",
        to: "vendor",
        context: "node_modules"
      },
      {
        from: "font-awesome/css",
        to: "vendor/font-awesome/css",
        context: "node_modules"
      },
      {
        from: "font-awesome/fonts",
        to: "vendor/font-awesome/fonts",
        context: "node_modules"
      }
    ])
  ]
};
