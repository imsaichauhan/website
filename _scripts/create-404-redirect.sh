#!/bin/bash
# Post-render script to create 404.html redirect

cat > _site/404.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="0; url=/404/">
  <link rel="canonical" href="/404/">
</head>
<body>
  <script>
    window.location.href = "/404/";
  </script>
</body>
</html>
EOF

echo "Created 404.html redirect"
