import { Auth } from '@lib/auth';
import { Controller, Post, Res } from '@nestjs/common';
import { ApiTags } from '@nestjs/swagger';
import { Response } from 'express';

@Controller('auth')
@ApiTags('auth')
export class AuthController {
  @Post('/sign-in')
  async signIn(@Res({ passthrough: true }) response: Response): Promise<void> {
    response.cookie('authorization', 'walletAddress');
  }

  @Auth()
  @Post('/sign-out')
  async signOut(@Res({ passthrough: true }) response: Response): Promise<void> {
    response.clearCookie('authorization');
  }
}
