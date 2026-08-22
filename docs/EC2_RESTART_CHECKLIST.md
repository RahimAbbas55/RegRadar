# EC2 Restart Checklist

Since we release the Elastic IP to save cost (~$3.60/month while stopped), every time
the instance is stopped and restarted, it gets a NEW public IP and public DNS name.
These three things must be updated to match, in this order:

## 1. Start the instance and get the new IP
```bash
aws ec2 start-instances --instance-ids i-07e87c92fa2f37fb1 --region us-east-1
aws ec2 wait instance-running --instance-ids i-07e87c92fa2f37fb1 --region us-east-1

aws ec2 describe-instances --instance-ids i-07e87c92fa2f37fb1 \
  --query 'Reservations[0].Instances[0].[PublicIpAddress,PublicDnsName]' \
  --output text --region us-east-1
```

## 2. Update GitHub Actions secret
GitHub → RegRadar → Settings → Secrets and variables → Actions → `EC2_HOST` → Update
→ set to the new PublicIpAddress

## 3. Update CloudFront origin domain
```bash
aws cloudfront get-distribution-config --id E3NQZ0TRX226BC > /tmp/current-dist-config.json
# note the ETag from the output
# edit the "EC2-regradar-backend" origin's DomainName to the new PublicDnsName
aws cloudfront update-distribution --id E3NQZ0TRX226BC \
  --distribution-config file:///tmp/updated-dist-config.json \
  --if-match <ETAG_FROM_ABOVE>
```
(Takes 5-15 min to redeploy globally)

## 4. Update backend CORS (only if the CloudFront domain itself ever changes — it won't from an IP change alone, skip this step for routine restarts)

## 5. Verify containers came back up
```bash
ssh -i ~/regradar-ec2-key.pem ec2-user@<NEW_IP> "sudo docker ps -a"
```
Both regradar-qdrant and regradar-backend should show "Up" (restart policy handles this
automatically) — if not, restart manually:
```bash
sudo docker start regradar-qdrant regradar-backend
```

## 6. Test end-to-end
```bash
curl http://<NEW_IP>:8000/health
```
Then visit https://d2wwendushtv6i.cloudfront.net and confirm a real query works.