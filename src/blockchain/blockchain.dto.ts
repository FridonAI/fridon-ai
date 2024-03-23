import { BaseDto } from '@lib/common';
import { ApiProperty } from '@nestjs/swagger';
import { IsNotEmpty, IsNumber, IsString } from 'class-validator';
import { OperationType, ProviderType } from './utils/types';
import { Transform } from 'class-transformer';

// Default Transfer Reponse Dto
export class TransactionDataResponseDto {
  @ApiProperty({ example: {} })
  serializedTx: Uint8Array;
}

export class BaseTransactionResponseDto extends BaseDto<BaseTransactionResponseDto> {
  @ApiProperty({ example: true })
  status: boolean;

  @ApiProperty({ example: 'Success' })
  message: string;

  @ApiProperty({ type: TransactionDataResponseDto })
  data: TransactionDataResponseDto;
}

// Transfer
export class TransferTokenRequestBodyDto {
  @IsString()
  @IsNotEmpty()
  @ApiProperty({ example: '6Uj4wUCtHKieQ7upZivYnQZnzGdfg3xEbSV5YJmsiV3e' })
  // toto: custom validation for walleteAddress
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
  operation: OperationType;

  @IsString()
  @IsNotEmpty()
  @ApiProperty({ example: ProviderType.Kamino })
  @Transform(({ value }) => value.toLowerCase())
  provider: ProviderType;

  @IsString()
  @IsNotEmpty()
  @ApiProperty({ example: 'Sol' })
  @Transform(({ value }) => value.toLowerCase())
  currency: string;
}

export class DefiOperationResponseBodyDto extends BaseTransactionResponseDto {}

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
  @ApiProperty({ example: 'Kamino' })
  @Transform(({ value }) => value.toLowerCase())
  provider: string;
}

export class BalanceOperationResponseBodyDto extends BaseTransactionResponseDto {}
