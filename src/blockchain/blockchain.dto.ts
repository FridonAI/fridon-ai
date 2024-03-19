import { BaseDto } from '@lib/common';
import { ApiProperty } from '@nestjs/swagger';
import { IsNotEmpty, IsNumber, IsString } from 'class-validator';
import {
  OperationType,
  ProviderType,
  TransactionDataType,
} from './utils/types';

// Default Transfer Reponse Dto
export class BaseTransactionResponseDto extends BaseDto<BaseTransactionResponseDto> {
  @ApiProperty({ example: true })
  status: boolean;

  @ApiProperty({ example: 'Success' })
  message: string;

  @ApiProperty()
  data: TransactionDataType;
}

// Transfer
export class TransferTokenRequestBodyDto {
  @IsString()
  @IsNotEmpty()
  @ApiProperty({ example: 'EkgRcppmG4vmPtFgmxKawR7rdmgJ2Z3Z35J8Uhj3ageX' })
  // toto: custom validation for walleteAddress
  walletAddress: string;

  @IsString()
  @IsNotEmpty()
  @ApiProperty({ example: 'CM8PWG9RsC6DfPauGruCvThss1M5GPRdrsb2HXRnGyYc' })
  toAddress: string;

  @IsString()
  @IsNotEmpty()
  @ApiProperty({ example: 'DFL1zNkaGPWm1BqAVqRjCZvHmwTFrEaJtbzJWgseoNJh' })
  mintAddress: string;

  @IsNumber()
  @ApiProperty({ example: 10 })
  amount: number;
}

export class TransferTokenResponseDto extends BaseTransactionResponseDto {}

// Defi Operations
export class DefiOperationRequestBodyDto {
  @IsString()
  @IsNotEmpty()
  @ApiProperty({ example: 'EkgRcppmG4vmPtFgmxKawR7rdmgJ2Z3Z35J8Uhj3ageX' })
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
  provider: ProviderType;

  @IsString()
  @IsNotEmpty()
  @ApiProperty({ example: 'Dfl' })
  currency: string;
}

export class DefiOperationResponseBodyDto extends BaseTransactionResponseDto {}
