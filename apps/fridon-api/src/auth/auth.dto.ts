import { ApiProperty } from '@nestjs/swagger';
import { IsNotEmpty, IsString } from 'class-validator';

export class SignInDto {
  @IsString()
  @IsNotEmpty()
  @ApiProperty({ example: 'EkgRcppmG4vmPtFgmxKawR7rdmgJ2Z3Z35J8Uhj3ageX' })
  walletAddress: string;
}
