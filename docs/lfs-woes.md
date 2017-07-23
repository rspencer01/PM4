## Git LFS Woes

I ran into some problems with `git lfs` over the course of a couple of weeks.  The issue was that I was unable to upload my asset files to the LFS storage.  I had about 44MB of assets to upload and it would tank out at uploading about 3Mb.

The exact error was

~~~ shell
Git LFS: (0 of 4 files, 8 skipped) 0 B / 47.09 MB, 6.27 MB skipped
LFS: Put https://github-cloud.s3.amazonaws.com/alambic/media/147473055/ce/b2/ceb2...277?actor_id=2918499: read tcp 192.168.1.32:34475->52.216.1.192:443: i/o timeout
LFS: Put https://github-cloud.s3.amazonaws.com/alambic/media/147473055/c8/bd/c8bd...c93?actor_id=2918499: read tcp 192.168.1.32:34476->52.216.1.192:443: i/o timeout
LFS: Put https://github-cloud.s3.amazonaws.com/alambic/media/147473055/2f/b4/2fb4...f1a?actor_id=2918499: dial tcp: lookup github-cloud.s3.amazonaws.com on 127.0.1.1:53: read udp 127.0.0.1:39530->127.0.1.1:53: i/o timeout
LFS: Put https://github-cloud.s3.amazonaws.com/alambic/media/147473055/58/6e/586e...bb5?actor_id=2918499: read tcp 192.168.1.32:34477->52.216.1.192:443: i/o timeout
error: failed to push some refs to 'git@github.com:rspencer01/PM4.git'
~~~

Its worth noting that I don't have the fastest of internet connections (4MB/s at best).  However, I though this would be more than adequate for this.

The timeouts puzzled me.  It seemed like quite a strange issue, since it would upload continuosly for the first bit.

After a lot of retrying (which was purported to sometimes work) and considering removing the assets, I turned to other issues.  Sometime later, I was `wget`ing a file and I noticed that the download stalled several times for up to 20s.

This was it.  For whatever reason, my uploads and downloads periodically stall for a short while.  Indeed, upping the `activitytimeout` config option for `git lfs` solved the problem.

The final config that I am using is

~~~ ini
[lfs]
  dialtimeout = 600
  tlstimeout = 300
  activitytimeout = 60
  concurrenttransfers = 1
~~~

This makes me wonder though.  The default `activitytimeout` of `10` seems like way too little for me.  I have an [issue](https://github.com/git-lfs/git-lfs/issues/2430) out on the `git-lfs` repository, and will see if the limit might be increased.
