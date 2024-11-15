#!/usr/bin/env nu

def main [] {
    for file in (ls dummy_data) {
        let origin = $file.name
        let target = $origin
            | path basename
            | prepend [./layers/]
            | path join

        /usr/bin/env cp $origin $target

        print $"(timestamp) | (ansi pb)SIMULATE(ansi reset) | (ansi c)simulate_printer(ansi reset):(ansi c)main(ansi reset):(ansi c)13(ansi reset) - Finished printing layer ($target)"

        sleep 3sec
    }
}

def timestamp [] {
    date now
        | format date "%Y-%m-%d %H:%M:%S"
        | prepend [(ansi g)]
        | append [(ansi reset)]
        | str join
        | fill --alignment left --width 23
}
