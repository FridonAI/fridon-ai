import { HttpException, Logger } from '@nestjs/common';
import { InterfaceSnippet } from '../interface';
import { PublicKey } from '@metaplex-foundation/js';
import { TokenAmount } from 'src/blockchain/utils/tools/token-amount';
import {
  DONATION_ADDRESS,
  SOL_MINT_ADDRESS,
  SWAP_FEE_BPS,
  SWAP_REFERRAL_PROGRAM_ADDRESS,
  TRANSFER_FEE,
  WSOL_MINT_ADDRESS,
} from '../shared/contants';
import { getTokenSupply } from 'src/blockchain/utils/connection';
import {
  ConfigurationParameters,
  createJupiterApiClient,
  DefaultApi,
} from '@jup-ag/api';
import { VersionedTransaction } from '@solana/web3.js';
import { Registry } from 'src/data-providers/registry';

type Request = {
  walletAddress: string;
  fromToken: string;
  toToken: string;
  amount: number;
};

type Response = {
  serializedTx: number[];
};

@Registry('jupiter-swap')
export class SwapTokens extends InterfaceSnippet<Request, Response> {
  private logger = new Logger(SwapTokens.name);

  async execute(data: Request): Promise<Response> {
    this.logger.log(`Executing action: ${SwapTokens.name}`);

    const { walletAddress, fromToken, toToken, amount } = data;
    if (amount <= 0) {
      throw new HttpException('Amount must be greater than 0', 403);
    }

    try {
      new PublicKey(walletAddress);
    } catch (error) {
      throw new HttpException('Invalid wallet address', 403);
    }

    const accountInfo = await this.connection.getAccountInfo(
      new PublicKey(walletAddress),
    );

    if (!accountInfo) {
      throw new HttpException('Sol Account not found', 404);
    }

    const solBalance = new TokenAmount(accountInfo!.lamports, 9, true).toWei();
    if (solBalance.lt(TRANSFER_FEE)) {
      throw new HttpException(`Insufficient balance for Fees!`, 403);
    }

    const fromMintAddress = await this.tools.convertSymbolToMintAddress(
      this.tools.getCurrencySymbol(fromToken),
    );

    const toMintAddress = await this.tools.convertSymbolToMintAddress(
      this.tools.getCurrencySymbol(toToken),
    );

    const tokenBalance = await this.tools.getTokenBalanceSpl(
      this.connection,
      new PublicKey(walletAddress),
      new PublicKey(fromMintAddress),
    );

    if (parseFloat(tokenBalance.fixed()) < amount) {
      throw new HttpException('Insufficient balance', 403);
    }

    const tokenInfo = await getTokenSupply(fromMintAddress, this.connection);

    if (!tokenInfo) {
      throw new HttpException('Token not found', 404);
    }

    const decimals = tokenInfo.value.decimals;
    const amountBN = new TokenAmount(amount, decimals, false);

    const versionedTx = await this.swapTokens(
      walletAddress,
      fromMintAddress,
      toMintAddress,
      amountBN.toNumber(),
    );

    console.log('versionedTx', versionedTx.serialize());

    return {
      serializedTx: Object.values(versionedTx.serialize()),
    };
  }

  async swapTokens(
    walletAddress: string,
    fromToken: string,
    toToken: string,
    amount: number,
  ) {
    const jupiter = this.initializeJupiterClient({});

    const quote = await this.quote(jupiter, fromToken, toToken, amount);
    // todo: write checker if balance is enough.
    const inputMintAddress =
      quote.inputMint === WSOL_MINT_ADDRESS.toBase58()
        ? SOL_MINT_ADDRESS.toBase58()
        : quote.inputMint;

    inputMintAddress;

    // Fee Account
    const [feeAccount] = PublicKey.findProgramAddressSync(
      [
        Buffer.from('referral_ata'),
        DONATION_ADDRESS.toBuffer(), // your referral account public key
        new PublicKey(quote.outputMint).toBuffer(), // the token mint
      ],
      SWAP_REFERRAL_PROGRAM_ADDRESS, // the Referral Program
    );
    const accountInfo = await this.connection.getAccountInfo(feeAccount);

    try {
      const swapRes = await jupiter.swapPost({
        swapRequest: {
          userPublicKey: walletAddress,
          feeAccount: accountInfo ? feeAccount.toBase58() : undefined,
          quoteResponse: quote,
          dynamicComputeUnitLimit: true,
          prioritizationFeeLamports: 'auto',
        },
      });

      const txBuffer = Buffer.from(swapRes.swapTransaction, 'base64');

      return VersionedTransaction.deserialize(txBuffer);
    } catch (e) {
      console.error('Swap Failed', e);
      throw new HttpException('Swap failed', 500);
    }
  }

  private initializeJupiterClient(config: ConfigurationParameters): DefaultApi {
    return createJupiterApiClient(config);
  }

  private async quote(
    jupiter: DefaultApi,
    fromToken: string,
    toToken: string,
    amount: number,
  ) {
    try {
      const quote = await jupiter.quoteGet({
        inputMint: fromToken,
        outputMint: toToken,
        amount: amount,
        platformFeeBps: SWAP_FEE_BPS,
      });
      if (!quote) {
        throw new HttpException('Quote not found', 404);
      }

      return quote;
    } catch (e) {
      console.error('Quote Failed', e);
      throw new HttpException('Quote failed', 500);
    }
  }
}
