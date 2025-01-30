import { ApiProperty } from '@nestjs/swagger';
import { IsPublicKey } from '@lib/common';
import { IsOptional } from 'class-validator';

export class SignUpRequestDto {
  @ApiProperty({
    example: 'CM8PWG9RsC6DfPauGruCvThss1M5GPRdrsb2HXRnGyYc',
    description: 'Authorization Wallet Id',
  })
  @IsPublicKey()
  readonly walletId: string;

  @ApiProperty({
    example: '',
    description: 'Signature of the wallet',
  })
  @IsOptional()
  readonly signature: string;
}
