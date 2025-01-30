import { SetMetadata, UseGuards, applyDecorators } from '@nestjs/common';
import { ApiBearerAuth, ApiUnauthorizedResponse } from '@nestjs/swagger';
import { RolesGuard } from '../guards/auth.guard';

export enum Role {
  Admin = 'admin',
  User = 'user',
  Public = 'public', // optional
}

export function Auth(...roles: Role[]) {
  // console.log('Roles passed to Auth decorator:', roles);
  return applyDecorators(
    SetMetadata('roles', roles.length ? roles : [Role.Public]),
    UseGuards(RolesGuard),
    ApiBearerAuth(),
    ApiUnauthorizedResponse({ description: 'Unauthorized' }),
  );
}
