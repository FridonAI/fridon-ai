import { BadRequestException } from '@nestjs/common';

type ModelResponseSuccess = { vector: [number[]] };
type ModelResponseError = { error: string };

type ModelResponse = ModelResponseError | ModelResponseSuccess;

export class HuggingFaceAdapter {
  async getEmbeddings(arr: number[][]): Promise<ModelResponseSuccess> {
    const modelUrl =
      'https://kt60ga6c7qc0otgc.us-east-1.aws.endpoints.huggingface.cloud';

    const response = await fetch(modelUrl, {
      method: 'POST',
      headers: {
        Authorization: 'Bearer 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',
        Accept: 'application/json',
        'Content-type': 'application/json',
      },
      body: JSON.stringify({ inputs: arr }),
    });

    const result = (await response.json()) as ModelResponse;
    if ('error' in result) {
      throw new BadRequestException(`Hugging Face error: ${result.error}`);
    }

    return result;
  }
}
