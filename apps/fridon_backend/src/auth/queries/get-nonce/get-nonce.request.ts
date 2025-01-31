import { IsPublicKey } from '@lib/common';
import { ApiPropertyOptional } from '@nestjs/swagger';
import { IsNotEmpty, IsString } from 'class-validator';

export class GetNonceRequestDto {
  @ApiPropertyOptional({
    example: 'CM8PWG9RsC6DfPauGruCvThss1M5GPRdrsb2HXRnGyYc',
    description: 'Wallet Address to get Nonce.',
  })
  @IsString()
  @IsNotEmpty()
  @IsPublicKey()
  walletAddress!: string;
}
