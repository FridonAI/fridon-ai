import { Controller, Get, Query, UseGuards } from '@nestjs/common';
import { ApiTags } from '@nestjs/swagger';
import { ThrottlerGuard } from '@nestjs/throttler';
import { ProxyService } from './proxy.service';
import { GetOHLCVQueryDto, GetOHLCVResponseDto, GetTokensQueryDto, GetTokensResponseDto, OHLCVDto } from './proxy.dto';

@Controller('proxy')
@ApiTags('proxy')
@UseGuards(ThrottlerGuard)
export class ProxyController {
    constructor(private readonly proxyService: ProxyService) {}

    @Get('ohlcv')
    async getOHLCV(@Query() query: GetOHLCVQueryDto): Promise<GetOHLCVResponseDto> {
        const ohlcvData = await this.proxyService.getOHLCV(query.symbol, query.interval, query.startTime, query.endTime);
        return {
            data: ohlcvData.map((ohlcv) => ({
                t: ohlcv.timestamp,
                o: ohlcv.open,
                h: ohlcv.high,
                l: ohlcv.low,
                c: ohlcv.close,
                v: ohlcv.volume,
            }) as OHLCVDto),
        } as GetOHLCVResponseDto;
    }

    @Get('tokens')
    async getTokens(@Query() query: GetTokensQueryDto): Promise<GetTokensResponseDto> {
        const tokens = await this.proxyService.getTokens(query.keyword);
        return {
            data: tokens,
        } as GetTokensResponseDto;
    }
}
