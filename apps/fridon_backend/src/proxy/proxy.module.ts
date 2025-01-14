import { Module } from "@nestjs/common";
import { ProxyController } from "./proxy.controller";
import { ProxyService } from "./proxy.service";
import { BinanceAdapter } from "./adapters/ohlcv/binance.adapter";
import { BirdEyeAdapter } from "./adapters/ohlcv/bird-eye.adapter";
import { BinanceTokenListAdapter, JupiterTokenListAdapter } from "./adapters/token-list/token-list.adapter";
import { UpdateTokenList } from "./crons/update-token-list.cron";
import { ThrottlerModule } from "src/throttling/throttler.module";

@Module({
    imports: [
      ThrottlerModule,
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
