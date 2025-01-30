import { PublicKey } from '@solana/web3.js';
import {
  ValidationOptions,
  ValidatorConstraint,
  ValidatorConstraintInterface,
  registerDecorator,
} from 'class-validator';

@ValidatorConstraint({ async: false })
export class IsPublicKeyConstraint implements ValidatorConstraintInterface {
  validate(value: string): boolean {
    try {
      new PublicKey(value);
      return true;
    } catch {
      return false;
    }
  }

  defaultMessage(): string {
    return 'Invalid public key format';
  }
}

export function IsPublicKey(validationOptions?: ValidationOptions) {
  return function (object: object, propertyName: string) {
    registerDecorator({
      target: object.constructor,
      propertyName: propertyName,
      options: validationOptions,
      constraints: [],
      validator: IsPublicKeyConstraint,
    });
  };
}
