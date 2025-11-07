-- Social Media Marketing Campaign Tables
-- This migration adds social media campaign functionality to the CRM system

-- Table for social media campaigns
CREATE TABLE public.social_media_campaigns (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  name text NOT NULL,
  platform text NOT NULL,
  target_segment text NOT NULL,
  campaign_objective text NULL,
  created_at timestamp without time zone NULL DEFAULT now(),
  status text NULL DEFAULT 'draft',
  CONSTRAINT social_media_campaigns_pkey PRIMARY KEY (id),
  CONSTRAINT social_media_campaigns_platform_check CHECK (
    platform = ANY (
      ARRAY[
        'facebook'::text,
        'linkedin'::text,
        'instagram'::text,
        'twitter'::text
      ]
    )
  ),
  CONSTRAINT social_media_campaigns_status_check CHECK (
    status = ANY (
      ARRAY[
        'draft'::text,
        'active'::text,
        'paused'::text,
        'completed'::text
      ]
    )
  ),
  CONSTRAINT social_media_campaigns_target_segment_check CHECK (
    target_segment = ANY (
      ARRAY[
        'Champion'::text,
        'Recent Customer'::text,
        'Frequent Buyer'::text,
        'Big Spender'::text,
        'At Risk'::text,
        'Others'::text
      ]
    )
  )
) TABLESPACE pg_default;

ALTER TABLE social_media_campaigns ENABLE ROW LEVEL SECURITY;

-- Table for generated social media posts
CREATE TABLE public.social_media_posts (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  campaign_id uuid NOT NULL,
  platform text NOT NULL,
  post_content text NOT NULL,
  post_tone text NULL,
  hashtags text NULL,
  generated_at timestamp without time zone NULL DEFAULT now(),
  CONSTRAINT social_media_posts_pkey PRIMARY KEY (id),
  CONSTRAINT social_media_posts_campaign_id_fkey FOREIGN KEY (campaign_id) 
    REFERENCES social_media_campaigns (id) ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT social_media_posts_platform_check CHECK (
    platform = ANY (
      ARRAY[
        'facebook'::text,
        'linkedin'::text,
        'instagram'::text,
        'twitter'::text
      ]
    )
  ),
  CONSTRAINT social_media_posts_tone_check CHECK (
    post_tone = ANY (
      ARRAY[
        'professional'::text,
        'casual'::text,
        'friendly'::text,
        'promotional'::text,
        'educational'::text
      ]
    )
  )
) TABLESPACE pg_default;

ALTER TABLE social_media_posts ENABLE ROW LEVEL SECURITY;

-- Table to link campaigns with target audience (customers in specific segments)
CREATE TABLE public.campaign_audience (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  campaign_id uuid NOT NULL,
  customer_id bigint NOT NULL,
  segment text NOT NULL,
  added_at timestamp without time zone NULL DEFAULT now(),
  CONSTRAINT campaign_audience_pkey PRIMARY KEY (id),
  CONSTRAINT campaign_audience_campaign_id_fkey FOREIGN KEY (campaign_id) 
    REFERENCES social_media_campaigns (id) ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT campaign_audience_customer_id_fkey FOREIGN KEY (customer_id) 
    REFERENCES customers ("Customer ID") ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT campaign_audience_unique UNIQUE (campaign_id, customer_id)
) TABLESPACE pg_default;

ALTER TABLE campaign_audience ENABLE ROW LEVEL SECURITY;

-- Create indexes for better performance
CREATE INDEX idx_social_media_campaigns_platform ON social_media_campaigns(platform);
CREATE INDEX idx_social_media_campaigns_target_segment ON social_media_campaigns(target_segment);
CREATE INDEX idx_social_media_campaigns_status ON social_media_campaigns(status);
CREATE INDEX idx_social_media_posts_campaign_id ON social_media_posts(campaign_id);
CREATE INDEX idx_campaign_audience_campaign_id ON campaign_audience(campaign_id);
CREATE INDEX idx_campaign_audience_segment ON campaign_audience(segment);
