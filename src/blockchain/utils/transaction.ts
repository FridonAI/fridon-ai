import { PublicKey, PublicKeyInitData, TransactionInstruction, TransactionMessage } from "@solana/web3.js";
import { createTransferInstructions, generateAssociatedTokenAccountInstructionsIfNeeded } from "./insturction";
import { getLatestBlockHash } from "./connection";

export async function generateTransferTransaction(
    from: PublicKeyInitData,
    to: PublicKeyInitData,
    mintAddress: string,
    amount: number
) {
    const payer = from;

    const txInstructions: TransactionInstruction[] = [];

    // Create token account if needed.
    const createAssociatedTokenInstructions =
        await generateAssociatedTokenAccountInstructionsIfNeeded(
            from,
            to,
            payer,
        );

    if (!!createAssociatedTokenInstructions) txInstructions.push(createAssociatedTokenInstructions);

    // Create Transfer instructions
    txInstructions.push(
        await createTransferInstructions(from, to, mintAddress, amount),
    );

    const message = new TransactionMessage({
        instructions: txInstructions,
        payerKey: new PublicKey(payer),
        recentBlockhash: (await getLatestBlockHash()).blockhash,
    });

    return message;
}
