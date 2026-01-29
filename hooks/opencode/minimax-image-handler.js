/**
 * MiniMax Image Handler Hook
 * 
 * Automatically uses MiniMax's understand_image when user attaches images
 * Works like Claude Opus - seamless image analysis
 */

export default {
  name: "minimax-image-handler",
  description: "Automatically analyze images with MiniMax understand_image",
  version: "1.0.0",

  // Hook into message processing - before the AI sees it
  hooks: {
    /**
     * PreToolUse: Intercept before AI decides what tool to use
     * Check if message has image attachments
     */
    async PreMessage(context) {
      const { message, attachments } = context;

      // Check if there are any image attachments
      const imageAttachments = attachments?.filter(att => 
        att.type === 'image' || 
        /\.(jpg|jpeg|png|gif|webp)$/i.test(att.path || att.url || att.name || '')
      );

      if (!imageAttachments || imageAttachments.length === 0) {
        return context; // No images, continue normally
      }

      // Extract user's question/prompt
      const userPrompt = message?.content || message?.text || "Please analyze this image";

      // Process each image with MiniMax
      const analyses = [];
      for (const img of imageAttachments) {
        const imageSource = img.url || img.path || img.filePath;
        
        if (!imageSource) {
          console.warn('[MiniMax Hook] Could not determine image source:', img);
          continue;
        }

        try {
          console.log('[MiniMax Hook] Analyzing image:', imageSource);
          
          // Call MiniMax understand_image via MCP
          const result = await context.mcp.call('MiniMax', 'understand_image', {
            prompt: userPrompt,
            image_url: imageSource
          });

          analyses.push({
            source: imageSource,
            analysis: result
          });

        } catch (error) {
          console.error('[MiniMax Hook] Error analyzing image:', error);
          analyses.push({
            source: imageSource,
            error: error.message
          });
        }
      }

      // Inject MiniMax analysis results into the context
      // So the AI can use them in its response
      if (analyses.length > 0) {
        const analysisText = analyses.map((a, idx) => {
          if (a.error) {
            return `\n**Image ${idx + 1}** (${a.source}):\nError: ${a.error}`;
          }
          return `\n**Image ${idx + 1}** (${a.source}):\n${a.analysis}`;
        }).join('\n\n');

        // Add to context as system message or augment user message
        context.additionalContext = (context.additionalContext || '') + 
          `\n\n---\n**[MiniMax Image Analysis]**\n${analysisText}\n---\n`;
        
        console.log('[MiniMax Hook] Added image analysis to context');
      }

      return context;
    },

    /**
     * Notification: Show user that MiniMax is being used
     */
    async Notification(context) {
      const { type, message } = context;

      if (type === 'image-attached') {
        return {
          ...context,
          message: '🖼️ MiniMax is analyzing your image...'
        };
      }

      return context;
    }
  },

  // Configuration
  config: {
    // Enable/disable the hook
    enabled: true,
    
    // Auto-analyze images by default
    autoAnalyze: true,
    
    // Max image size (20MB as per MiniMax spec)
    maxImageSize: 20 * 1024 * 1024,
    
    // Supported formats
    supportedFormats: ['jpg', 'jpeg', 'png', 'gif', 'webp'],
    
    // Default prompt if user doesn't provide one
    defaultPrompt: "Please analyze this image and describe what you see. Include any relevant details, text, diagrams, or issues you notice."
  }
};
