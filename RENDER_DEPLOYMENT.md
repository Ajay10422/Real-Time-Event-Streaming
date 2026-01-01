# Render Deployment Guide

This guide explains how to deploy the Real-Time ML Pipeline to Render.

## Architecture Overview

The deployment uses a **simplified single-service architecture** for Render:

- **Single Web Service**: Runs all components in one container
  - Producer (data ingestion)
  - Bronze Consumer (raw data → Parquet)
  - Silver Consumer (data cleaning & transformation)
  - Trainer (model retraining)
  - Dashboard (Streamlit UI)

- **Mock Kafka**: Uses an in-memory message queue instead of running a full Kafka broker
  - Eliminates the need for separate Kafka infrastructure
  - Perfect for demos and small-scale deployments
  - Automatically falls back if real Kafka is unavailable

## Deployment Steps

### Option 1: Deploy from GitHub (Recommended)

1. **Push your code to GitHub**
   ```bash
   git push origin main
   ```

2. **Create a new Web Service on Render**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect the `render.yaml` configuration

3. **Deploy**
   - Click "Create Web Service"
   - Render will build and deploy automatically
   - Wait for deployment to complete (~5-10 minutes)

4. **Access Your Dashboard**
   - Once deployed, click on the service URL
   - You should see the Streamlit dashboard
   - Metrics will start appearing as the pipeline processes data

### Option 2: Deploy with render.yaml Blueprint

1. **From Render Dashboard**
   - Click "New +" → "Blueprint"
   - Connect your repository
   - Render will detect `render.yaml` automatically

2. **Review Configuration**
   - Service Name: `ml-pipeline-dashboard`
   - Plan: Starter (free tier compatible)
   - Disk: 1GB persistent storage

3. **Deploy**
   - Click "Apply"
   - Monitor deployment logs

## Environment Variables

The deployment uses these environment variables (already configured in `render.yaml`):

| Variable | Value | Description |
|----------|-------|-------------|
| `USE_MOCK_KAFKA` | `true` | Enables mock Kafka (no external broker needed) |
| `KAFKA_BOOTSTRAP` | `localhost:9092` | Kafka connection (not used with mock) |
| `KAFKA_TOPIC` | `energuide-events` | Topic name for events |
| `PYTHONUNBUFFERED` | `1` | Enables real-time logging |

## Using Real Kafka (Optional)

If you want to use a real Kafka service instead of mock:

1. **Set up external Kafka** (choose one):
   - [Upstash Kafka](https://upstash.com/) - Free tier available
   - [CloudKarafka](https://www.cloudkarafka.com/) - Free tier available
   - Self-hosted Kafka

2. **Update environment variables in Render**:
   ```
   USE_MOCK_KAFKA=false
   KAFKA_BOOTSTRAP=your-kafka-server:9092
   ```

3. **Redeploy** the service

## Troubleshooting

### Deployment Fails

**Check build logs**:
- Go to Render Dashboard → Your Service → Logs
- Look for Python dependency errors
- Ensure all requirements are installed

**Common issues**:
- Memory limits: Upgrade from free tier if needed
- Build timeout: Try deploying during off-peak hours

### Application Crashes

**View runtime logs**:
```
Render Dashboard → Service → Logs
```

**Check for**:
- Python errors in startup
- Missing data directories (auto-created by `start_all.sh`)
- Port binding issues (should use `$PORT` from Render)

### Dashboard Shows No Data

**Verify services are running**:
- Check logs for "Starting producer...", "Starting trainer...", etc.
- All background services should start before dashboard

**Wait a few minutes**:
- First training requires minimum 20 rows
- Producer sends 2 rows every 2 seconds
- First metrics appear after ~30-60 seconds

### Disk Issues

**Check disk usage**:
- Render Dashboard → Service → Disk
- Default: 1GB should be sufficient for demo
- Upgrade if needed for larger datasets

## Performance Optimization

### For Production Use

1. **Separate Services**: Split into multiple services
   - Separate Kafka broker (use managed service)
   - Dedicated workers for each consumer
   - Separate dashboard service

2. **Scale Resources**:
   - Upgrade to paid plans for more CPU/RAM
   - Increase disk size for larger datasets
   - Enable autoscaling for high traffic

3. **Database for Metrics**:
   - Store metrics in PostgreSQL instead of CSV
   - Better for high-frequency updates
   - Easier to query and analyze

## Cost Estimation

**Free Tier**:
- 750 hours/month of compute (one service)
- 1GB persistent disk
- Automatic sleep after 15min inactivity
- **Cost**: Free

**Paid Plans** (if needed):
- Starter: $7/month - No sleep, better performance
- Standard: $25/month - More resources
- Pro: $85/month - Autoscaling, priority support

## Monitoring

### View Logs
```
Render Dashboard → Your Service → Logs
```

### Check Service Health
```
Render Dashboard → Your Service → Events
```

### Metrics Dashboard
- Access via the service URL
- Real-time R² and MAE metrics
- Interactive charts with Altair

## Next Steps

- Monitor your deployment in Render Dashboard
- Check the Streamlit dashboard URL
- Watch metrics update in real-time
- Customize the pipeline for your use case

## Support

- [Render Documentation](https://render.com/docs)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Project Issues](https://github.com/Ajay10422/Real-Time-Event-Streaming/issues)
