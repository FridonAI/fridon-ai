import { Auth } from '@lib/auth';
import { Body, Controller, Post, Res } from '@nestjs/common';
import { ApiTags } from '@nestjs/swagger';
import { Response } from 'express';
import { SignInDto } from './auth.dto';

@Controller('auth')
@ApiTags('auth')
export class AuthController {
  @Post('/sign-in')
  async signIn(
    @Body() body: SignInDto,
    @Res({ passthrough: true }) response: Response,
  ): Promise<void> {
    response.cookie('authorization', body.walletAddress);
  }

  @Auth()
  @Post('/sign-out')
  async signOut(@Res({ passthrough: true }) response: Response): Promise<void> {
    response.clearCookie('authorization');
  }
}
