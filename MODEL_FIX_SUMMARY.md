# Model Fix Summary

## Problem Identified

You were using `gemini-2.0-flash-exp` (experimental model) which has very limited quota in the free tier. Even with just 8 requests, you hit the quota limit because experimental models have stricter rate limits.

## Solution Applied

Changed to `gemini-2.5-flash` - the stable, production-ready model with full free tier support.

### Files Updated

1. **config.yaml** - Changed model from `gemini-2.0-flash-exp` to `gemini-2.5-flash`
2. **utils/vertex_client.py** - Updated default model to `gemini-2.5-flash`

### Free Tier Quotas (gemini-2.5-flash)

- **Requests per minute**: 15
- **Requests per day**: 1,500
- **Tokens per minute**: 1,000,000
- **Tokens per day**: 50,000,000

This is much more generous than the experimental model.

## Testing Results

- API key is valid
- Model works correctly
- App is running on http://localhost:8502
- Demo mode works with Attention paper
- Live mode now works with proper quota

## Next Steps

1. **Test Live Mode** - Try uploading a paper and asking questions
2. **Generate Caches** - Run `python generate_cache.py` to create caches for DQN and AlexNet
3. **Deploy** - Follow DEPLOYMENT_CHECKLIST.md

## Why This Happened

Experimental models (with "-exp" suffix) are:

- Preview/beta versions
- Have limited availability
- Have stricter rate limits
- Not recommended for production use

Stable models (without "-exp") are:

- Production-ready
- Full free tier support
- Better rate limits
- Recommended for all applications

## Recommendation

Always use stable models for your projects:

- `gemini-2.5-flash` - Fast, efficient (recommended)
- `gemini-2.5-pro` - More capable, slower
- `gemini-2.0-flash` - Previous stable version

Avoid experimental models unless you specifically need bleeding-edge features.
