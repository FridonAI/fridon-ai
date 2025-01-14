import { ApiProperty } from "@nestjs/swagger";
import { IsNotEmpty, IsNumber } from "class-validator";

import { IsString } from "class-validator";
import { Transform } from "class-transformer";

export class GetOHLCVQueryDto {
    @IsString()
    @IsNotEmpty()
    @ApiProperty({ example: 'btc' })
    symbol: string;

    @IsString()
    @IsNotEmpty()
    @ApiProperty({ example: '30m' })
    interval: '30m' | '1h' | '4h' | '1d';

    @Transform(({ value }) => Number(value))
    @IsNumber()
    @IsNotEmpty()
    @ApiProperty({ example: 1710000000 })
    startTime: number;

    @Transform(({ value }) => Number(value))
    @IsNumber()
    @IsNotEmpty()
    @ApiProperty({ example: 1710000000 })
    endTime: number;
}

export class OHLCVDto {
    @ApiProperty({ example: 1710000000 })
    t: number;

    @ApiProperty({ example: 10000 })
    o: number;

    @ApiProperty({ example: 10000 })
    h: number;

    @ApiProperty({ example: 10000 })
    l: number;

    @ApiProperty({ example: 10000 })
    c: number;

    @ApiProperty({ example: 10000 })
    v: number;
}

export class GetOHLCVResponseDto {
    @ApiProperty({ type: OHLCVDto })
    data: OHLCVDto[];
}

export class GetTokensQueryDto {
    @IsString()
    @IsNotEmpty()
    @ApiProperty({ example: 'btc' })
    keyword: string;
}

export class GetTokensResponseDto {
    @ApiProperty({ type: String, isArray: true })
    data: string[];
}
