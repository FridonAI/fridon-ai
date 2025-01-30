import { Injectable, Logger } from '@nestjs/common';
import {
  GetSecretValueCommand,
  SecretsManagerClient,
} from '@aws-sdk/client-secrets-manager';

@Injectable()
export class SecretsService {
  private readonly logger = new Logger(SecretsService.name);
  private secretsManagerClient: SecretsManagerClient;
  private serverKeyPair: { pk: string; sk: string } | null = null;

  constructor() {
    this.secretsManagerClient = new SecretsManagerClient({
      region: 'eu-central-1',
    });
  }

  private async retrieveAuthKeyPair(): Promise<{ pk: string; sk: string }> {
    if (!process.env['SECRET_MANAGER_SERVER_KEY_PAIR_NAME']) {
      throw new Error(
        'SECRET_MANAGER_SERVER_KEY_PAIR_NAME environmental variable is not set!',
      );
    }
    const secretName = process.env['SECRET_MANAGER_SERVER_KEY_PAIR_NAME'];

    if (!this.serverKeyPair) {
      try {
        const command = new GetSecretValueCommand({ SecretId: secretName });
        const response = await this.secretsManagerClient.send(command);

        if (!response.SecretString) {
          throw new Error('SecretString not found in Secrets Manager response');
        }

        this.serverKeyPair = JSON.parse(response.SecretString);

        if (!this.serverKeyPair) {
          throw new Error('Invalid key pair retrieved from Secrets Manager');
        }

        if (!this.serverKeyPair.pk || !this.serverKeyPair.sk) {
          throw new Error('Invalid key pair retrieved from Secrets Manager');
        }
      } catch (error) {
        this.logger.error(
          'Error retrieving key pair from Secrets Manager',
          error,
        );
        throw new Error('Failed to retrieve key pair from Secrets Manager');
      }
    }

    return this.serverKeyPair;
  }

  public async retrieveAuthPublicKey(): Promise<string> {
    const { pk } = await this.retrieveAuthKeyPair();
    return pk;
  }

  public async retrieveAuthSecretKey(): Promise<string> {
    const { sk } = await this.retrieveAuthKeyPair();
    return sk;
  }
}
