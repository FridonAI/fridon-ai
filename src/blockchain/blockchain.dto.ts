import { ApiProperty } from '@nestjs/swagger';
import { IsNotEmpty, IsNumber, IsString } from 'class-validator';

export class TransferTokenDto {
  @IsString()
  @IsNotEmpty()
  @ApiProperty({ example: 'EkgRcppmG4vmPtFgmxKawR7rdmgJ2Z3Z35J8Uhj3ageX' })
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
