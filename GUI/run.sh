#! /usr/bin/env expect
spawn startx -- -layout Multihead
expect "Press Enter to continue" {send "\r"}
interact
