import { Injectable, Logger } from '@nestjs/common';
import { BinanceAdapter } from './adapters/ohlcv/binance.adapter';
import { BirdEyeAdapter } from './adapters/ohlcv/bird-eye.adapter';
import { OHLCV } from './adapters/ohlcv/ohlcv.adapter';
import { BinanceTokenListAdapter, JupiterTokenListAdapter } from './adapters/token-list/token-list.adapter';

@Injectable()
export class ProxyService {
    private readonly logger = new Logger(ProxyService.name);

    constructor(
        private readonly binanceAdapter: BinanceAdapter,
        private readonly birdeyeAdapter: BirdEyeAdapter,
        private readonly jupiterTokenListAdapter: JupiterTokenListAdapter,
        private readonly binanceTokenListAdapter: BinanceTokenListAdapter,
    ) { }

    async getOHLCV(symbol: string, interval: '30m' | '1h' | '4h' | '1d', startTime: number, endTime: number): Promise<OHLCV[]> {
        try {
            this.logger.log(`Getting OHLCV for ${symbol} from Binance`);
            return await this.binanceAdapter.getOHLCV(symbol, interval, startTime, endTime);
        } catch (error) {
            const binanceError = error as Error;
            this.logger.log(`Getting OHLCV for ${symbol} from Birdeye`);
            try {
                return await this.birdeyeAdapter.getOHLCV(symbol, interval, startTime, endTime);
            } catch (error) {
                const birdeyeError = error as Error;
                this.logger.error(`Failed to get OHLCV from both providers: Binance (${binanceError.message}), Birdeye (${birdeyeError.message})`);
                throw birdeyeError;
            }
        }
    }

    async getTokens(keyword: string): Promise<string[]> {
        const tokenList = await this.jupiterTokenListAdapter.getTokenList();
        const binanceTokenList = this.binanceTokenListAdapter.getTokenList();
        return Array.from(new Set([...tokenList.map(item => (item.symbol.startsWith('$') ? item.symbol.slice(1) : item.symbol).toUpperCase()), ...binanceTokenList]))
            .filter(token => token.toUpperCase().startsWith(keyword.toUpperCase()))
            .sort((a, b) => a.localeCompare(b));
    }
}
