import { Controller, Get, HttpStatus, Param } from '@nestjs/common';
import { ApiOperation, ApiResponse } from '@nestjs/swagger';
import { authRoutes } from 'src/auth/configs/app.routes';
import { AuthRepository } from 'src/auth/database/auth.repository';
import { GetNonceRequestDto } from './get-nonce.request';
import { GetNonceResponseDto } from './get-nonce.response-dto';

@Controller(authRoutes.root)
export class GetNonceController {
  constructor(private authRepository: AuthRepository) { }

  @Get(authRoutes.getNonce)
  @ApiOperation({ summary: 'Get Nonce', tags: ['Auth'] })
  @ApiResponse({
    status: HttpStatus.OK,
    type: GetNonceResponseDto,
  })
  @ApiResponse({ status: HttpStatus.NOT_FOUND })
  async getNonce(@Param() param: GetNonceRequestDto) {
    const { walletAddress } = param;

    const result = await this.authRepository.getNonce(walletAddress);

    if (result) {
      return new GetNonceResponseDto({
        nonce: result.nonce,
        verifiedAt: result.verifiedAt ?? undefined,
      });
    }

    const tempNonce = await this.authRepository.createNonce(walletAddress, 20);

    return new GetNonceResponseDto({
      nonce: tempNonce.nonce,
    });
  }
}
