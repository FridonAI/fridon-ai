import { Module } from "@nestjs/common";
import { ThrottlerModule } from '@nestjs/throttler';
import { ProxyController } from "./proxy.controller";
import { ProxyService } from "./proxy.service";
import { BinanceAdapter } from "./adapters/ohlcv/binance.adapter";
import { BirdEyeAdapter } from "./adapters/ohlcv/bird-eye.adapter";
import { BinanceTokenListAdapter, JupiterTokenListAdapter } from "./adapters/token-list/token-list.adapter";
import { UpdateTokenList } from "./crons/update-token-list.cron";

@Module({
    imports: [
        ThrottlerModule.forRoot([{
            ttl: 1000, // 1 second
            limit: 15, // 15 requests per second
        }]),
    ],
    controllers: [ProxyController],
    providers: [ProxyService, BinanceAdapter, BirdEyeAdapter, JupiterTokenListAdapter, BinanceTokenListAdapter, UpdateTokenList],
    exports: [ProxyService, BinanceAdapter, BirdEyeAdapter, JupiterTokenListAdapter, BinanceTokenListAdapter],
})
export class ProxyModule {
    static forRoot() {
        return {
            module: ProxyModule,
            global: true,
        };
    }
}
