import { applyDecorators, UseGuards } from '@nestjs/common';
import { ApiCookieAuth, ApiUnauthorizedResponse } from '@nestjs/swagger';
import { AuthGuard } from '../guards/auth.guard';

export function Auth() {
  return applyDecorators(
    UseGuards(AuthGuard),
    ApiCookieAuth(),
    ApiUnauthorizedResponse({ description: 'Unauthorized' }),
  );
}
