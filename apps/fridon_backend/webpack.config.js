const CopyPlugin = require('copy-webpack-plugin');

const swcDefaultConfig =
  require('@nestjs/cli/lib/compiler/defaults/swc-defaults').swcDefaultsFactory()
    .swcOptions;

// copy
module.exports = {
  plugins: [
    new CopyPlugin({
      patterns: [
        {
          from: 'src/blockchain/cron/coins-list.json',
          to: 'blockchain/cron/coins-list.json',
        },
        {
          from: 'src/blockchain/cron/coins-list-new.json',
          to: 'blockchain/cron/coins-list-new.json',
        },
      ],
    }),
  ],
  module: {
    rules: [
      {
        test: /\.ts$/,
        exclude: /node_modules/,
        use: {
          loader: 'swc-loader',
          options: swcDefaultConfig,
        },
      },
    ],
  },
};
