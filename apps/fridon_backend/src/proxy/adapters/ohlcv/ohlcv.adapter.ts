export interface OHLCV {
    timestamp: number;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
}

export interface OHLCVAdapter {
  getOHLCV(symbol: string, interval: '30m' | '1h' | '4h' | '1d', startTime: number, endTime: number): Promise<OHLCV[]>;
}
