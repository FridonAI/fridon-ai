import { Module } from '@nestjs/common';
import { ProxyController } from './proxy.controller';
import { ProxyService } from './proxy.service';
import { BinanceAdapter } from './adapters/ohlcv/binance.adapter';
import { BirdEyeAdapter } from './adapters/ohlcv/bird-eye.adapter';
import { BybitAdapter } from './adapters/ohlcv/bybit.adapter';
import {
  BinanceTokenListAdapter,
  BybitTokenListAdapter,
  JupiterTokenListAdapter,
} from './adapters/token-list/token-list.adapter';
import { UpdateTokenList } from './crons/update-token-list.cron';
// import { ThrottlerModule } from "@nestjs/throttler";

@Module({
  imports: [
    // ThrottlerModule.forRoot([{
    //     name: 'proxy',
    //     ttl: 10000000,
    //     limit: 1,
    // }]),
  ],
  controllers: [ProxyController],
  providers: [
    ProxyService,
    BinanceAdapter,
    BirdEyeAdapter,
    BybitAdapter,
    JupiterTokenListAdapter,
    BinanceTokenListAdapter,
    BybitTokenListAdapter,
    UpdateTokenList,
  ],
  exports: [
    ProxyService,
    BinanceAdapter,
    BirdEyeAdapter,
    BybitAdapter,
    JupiterTokenListAdapter,
    BinanceTokenListAdapter,
    BybitTokenListAdapter,
  ],
})
export class ProxyModule {}
