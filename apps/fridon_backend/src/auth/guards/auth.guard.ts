import {
  BadRequestException,
  CanActivate,
  ExecutionContext,
  Injectable,
  UnauthorizedException,
} from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { Role } from '../decorators/auth.decorator';
import { ClaimsType } from '../decorators/claims.decorator';
import { SecretsService } from '../domain-services/secrets.service';
import { verify } from '../domain/utils';

@Injectable()
export class RolesGuard implements CanActivate {
  constructor(
    private reflector: Reflector,
    private secretsService: SecretsService,
  ) {}

  async canActiveWs(token: string): Promise<ClaimsType> {
    let claims: ClaimsType | undefined;
    try {
      claims = this.parseAuthTokenToClaims(token);
    } catch (error) {
      console.log('error', error);
      throw new UnauthorizedException('Invalid token');
    }

    if (!claims) {
      throw new UnauthorizedException('No user details found.');
    }

    const now = Math.floor(Date.now() / 1000);
    if (now > claims.exp) {
      throw new UnauthorizedException('Token has expired');
    }

    // 2. verify issuer
    const givenIssuer = claims.iss;
    const serverPublicKey = await this.secretsService.retrieveAuthPublicKey();
    if (givenIssuer !== serverPublicKey) {
      throw new UnauthorizedException('Invalid issuer');
    }

    // 3. verify server signature
    const { serverSig, ...claimsWithoutServerSig } = claims;

    if (
      !verify(JSON.stringify(claimsWithoutServerSig), serverSig, claims.iss)
    ) {
      throw 'Server signature verification failed';
    }

    return claims;
  }

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const stage = process.env['STAGE'];
    const requiredRoles = this.reflector.get<string[]>(
      'roles',
      context.getHandler(),
    );
    // const requiredRoles = this.reflector.get('roles', context.getHandler());

    const request = context.switchToHttp().getRequest();

    // Extract claims
    try {
      request.claims = this.getClaims(request);
    } catch (error) {
      if (requiredRoles.includes(Role.Public)) {
        return true; // Continue for public routes even if there's no token or invalid token
      }
      console.log('error', error);
      throw new UnauthorizedException('Invalid token');
    }

    if (requiredRoles.includes(Role.Public)) {
      return true;
    }

    if (!request.claims) {
      throw new UnauthorizedException('No user details found.');
    }

    const now = Math.floor(Date.now() / 1000);
    if (now > request.claims.exp) {
      throw new UnauthorizedException('Token has expired');
    }

    // 2. verify issuer
    const givenIssuer = request.claims.iss;
    const serverPublicKey = await this.secretsService.retrieveAuthPublicKey();
    if (givenIssuer !== serverPublicKey) {
      throw new UnauthorizedException('Invalid issuer');
    }

    // 3. verify server signature
    const { serverSig, ...claimsWithoutServerSig } = request.claims;

    if (
      !verify(
        JSON.stringify(claimsWithoutServerSig),
        serverSig,
        request.claims.iss,
      )
    ) {
      throw 'Server signature verification failed';
    }

    if (requiredRoles.includes(Role.Admin)) {
      console.log('request.user?.userType', request.claims.userType);
      if (request.claims.userType === Role.Admin) {
        return true;
      } else if (
        stage === 'develop' &&
        request.claims.sub === 'CM8PWG9RsC6DfPauGruCvThss1M5GPRdrsb2HXRnGyYc' // todo: we can remove this and pass everything on develop environment.
      ) {
        return true;
      }
      throw new UnauthorizedException(
        'Access denied - insufficient permissions.',
      );
    }

    return true;
  }

  private getClaims(request: Request): ClaimsType {
    // @ts-expect-error: This is not a valid type
    const authToken = request.headers['authorization'];
    if (!authToken)
      throw new UnauthorizedException('No authorization token found');

    return this.parseAuthTokenToClaims(authToken);
  }

  private parseAuthTokenToClaims(authToken: string): ClaimsType {
    const claimsStr = Buffer.from(authToken, 'base64').toString();
    try {
      return JSON.parse(claimsStr);
    } catch (error: any) {
      console.log('error', error);
      throw new BadRequestException('Failed to parse token');
    }
  }
}
