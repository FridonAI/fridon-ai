import { BaseDto, WrapperType } from '@lib/common';
import { ApiProperty } from '@nestjs/swagger';
import { IsNotEmpty, IsNumber, IsString } from 'class-validator';
import {
  BalanceOperationType,
  BalanceProviderType,
  OperationType,
  PointsProviderType,
  ProviderType,
  SymmetryOperationType,
} from './utils/types';
import { Transform } from 'class-transformer';

export class CoinSimilarityResponseDto extends BaseDto<CoinSimilarityResponseDto> {
  @ApiProperty({
    example: {
      data: [
        {
          symbol: 'Sol',
          address: 'So11111111111111111111111111111111111111112',
          chain: 'solana',
        },
      ],
    },
  })
  data: {
    symbol: string;
    address: string;
    chain: string;
  }[];
}
export class CoinSimilarityRequestDto {
  @IsString()
  @IsNotEmpty()
  @ApiProperty({ example: 'sol' })
  coin: string;

  @IsNumber()
  @IsNotEmpty()
  @ApiProperty({
    example: parseInt(`${new Date().getTime() / 1000 - 60 * 60 * 24}`),
  })
  from: number;

  @IsNumber()
  @IsNotEmpty()
  @ApiProperty({ example: parseInt(`${new Date().getTime() / 1000}`) })
  to: number;

  @IsNumber()
  @IsNotEmpty()
  @ApiProperty({ example: 1 })
  topK: number;
}

// Default Transfer Response Dto
export class TransactionDataResponseDto {
  @ApiProperty({ example: {} })
  serializedTx: number[];
}

export class BaseTransactionResponseDto extends BaseDto<BaseTransactionResponseDto> {
  @ApiProperty({ type: TransactionDataResponseDto })
  data: TransactionDataResponseDto;
}

// Points
export class PointsRequestBodyDto {
  @IsString()
  @IsNotEmpty()
  @ApiProperty({ example: '6Uj4wUCtHKieQ7upZivYnQZnzGdfg3xEbSV5YJmsiV3e' })
  walletAddress: string;

  @IsString()
  @IsNotEmpty()
  @ApiProperty({ example: PointsProviderType.All })
  @Transform(({ value }) => value.toLowerCase())
  provider: WrapperType<PointsProviderType>;
}

export class PointsDto extends BaseDto<PointsResponseDto> {
  @ApiProperty({ example: 10 })
  points: number;

  @ApiProperty({ example: PointsProviderType.All })
  provider: PointsProviderType;

  @ApiProperty({ example: '6Uj4wUCtHKieQ7upZivYnQZnzGdfg3xEbSV5YJmsiV3e' })
  walletAddress: string;
}

export class PointsResponseDto extends BaseDto<PointsResponseDto> {
  @ApiProperty({ type: PointsDto })
  data: PointsDto[];
}
// Symmetry
export class SymmetryBasketDto {
  @ApiProperty({ example: ['DFL', 'SOL'] })
  tokens: string[];

  @ApiProperty({ example: 2 })
  tvl: number;

  @ApiProperty({ example: 'LSD' })
  symbol: string;

  @ApiProperty({ example: 'Solana Defi Index' })
  name: string;
}

export class SymmetryBasketResponseDto extends BaseDto<SymmetryBasketResponseDto> {
  @ApiProperty({ type: SymmetryBasketDto, isArray: true })
  data: SymmetryBasketDto[];
}

export class SymmetryDefiOperationsRequestBodyDto {
  @IsString()
  @IsNotEmpty()
  @ApiProperty({ example: '6Uj4wUCtHKieQ7upZivYnQZnzGdfg3xEbSV5YJmsiV3e' })
  walletAddress: string;

  @IsString()
  @IsNotEmpty()
  @ApiProperty({ example: 'FSmR7QfFvtvqDMo4w5e39UtEubiY4q8T27wnNCJgQSxz' })
  basketAddress: string;

  @IsString()
  @IsNotEmpty()
  @ApiProperty({ example: 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v' })
  tokenAddress: string;

  @IsNumber()
  @ApiProperty({ example: 10 })
  amount: number;

  @IsString()
  @IsNotEmpty()
  @ApiProperty({ example: SymmetryOperationType.Deposit })
  @Transform(({ value }) => value.toLowerCase())
  operation: WrapperType<SymmetryOperationType>;
}

// Swap
export class SwapTokensRequestBodyDto {
  @IsString()
  @IsNotEmpty()
  @ApiProperty({ example: '6Uj4wUCtHKieQ7upZivYnQZnzGdfg3xEbSV5YJmsiV3e' })
  // toto: custom validation for wallet Address
  walletAddress: string;

  @IsString()
  @IsNotEmpty()
  @ApiProperty({ example: 'sol' })
  fromToken: string;

  @IsString()
  @IsNotEmpty()
  @ApiProperty({ example: 'usdc' })
  toToken: string;

  @IsNumber()
  @ApiProperty({ example: 10 })
  amount: number;
}

export class SwapTokensResponseDto extends BaseTransactionResponseDto {}

// Transfer
export class TransferTokenRequestBodyDto {
  @IsString()
  @IsNotEmpty()
  @ApiProperty({ example: '6Uj4wUCtHKieQ7upZivYnQZnzGdfg3xEbSV5YJmsiV3e' })
  // toto: custom validation for wallet Address
  walletAddress: string;

  @IsString()
  @IsNotEmpty()
  @ApiProperty({ example: 'CM8PWG9RsC6DfPauGruCvThss1M5GPRdrsb2HXRnGyYc' })
  toAddress: string;

  @IsString()
  @IsNotEmpty()
  @ApiProperty({ example: 'Dfl' })
  @Transform(({ value }) => value.toLowerCase())
  currency: string;

  @IsNumber()
  @ApiProperty({ example: 10 })
  amount: number;
}

export class TransferTokenResponseDto extends BaseTransactionResponseDto {}

// Defi Operations
export class DefiOperationRequestBodyDto {
  @IsString()
  @IsNotEmpty()
  @ApiProperty({ example: '6Uj4wUCtHKieQ7upZivYnQZnzGdfg3xEbSV5YJmsiV3e' })
  walletAddress: string;

  @IsNumber()
  @ApiProperty({ example: 10 })
  amount: number;

  @IsString()
  @IsNotEmpty()
  @ApiProperty({ example: OperationType.Supply })
  operation: WrapperType<OperationType>;

  @IsString()
  @IsNotEmpty()
  @ApiProperty({ example: ProviderType.Kamino })
  @Transform(({ value }) => value.toLowerCase())
  provider: WrapperType<ProviderType>;

  @IsString()
  @IsNotEmpty()
  @ApiProperty({ example: 'Sol' })
  @Transform(({ value }) => value.toLowerCase())
  currency: string;
}

export class TransactionResponseDto extends BaseTransactionResponseDto {}

// Balance Operations
export class BalanceOperationRequestBodyDto {
  @IsString()
  @IsNotEmpty()
  @ApiProperty({ example: '6Uj4wUCtHKieQ7upZivYnQZnzGdfg3xEbSV5YJmsiV3e' })
  walletAddress: string;

  @IsString()
  @ApiProperty({ example: 'Sol' })
  @Transform(({ value }) => value.toLowerCase())
  currency?: string | undefined;

  @IsString()
  @IsNotEmpty()
  @ApiProperty({ example: BalanceOperationType.Deposited })
  @Transform(({ value }) => value.toLowerCase())
  operation: WrapperType<BalanceOperationType>;

  @IsString()
  @IsNotEmpty()
  @ApiProperty({ example: BalanceProviderType.Kamino })
  @Transform(({ value }) => value.toLowerCase())
  provider: WrapperType<BalanceProviderType>;
}

export class BalanceDto {
  @ApiProperty({ example: 'Sol' })
  symbol: string;

  @ApiProperty({ example: '10' })
  amount: string;

  @ApiProperty({ example: '10' })
  value: string;

  @ApiProperty({ example: BalanceOperationType.Deposited })
  type?: string;
}
export class BalanceOperationResponseDto extends BaseDto<BalanceOperationResponseDto> {
  @ApiProperty({ type: BalanceDto })
  data: BalanceDto[];
}
