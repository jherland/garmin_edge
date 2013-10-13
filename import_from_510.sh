edgedir=$1
importdir=$2

die () {
	echo "$@"
	exit 1
}

test -f "$edgedir/Garmin/GarminDevice.xml" || die "$edgedir is not a Garmin device"
test -d "$importdir/.git" || die "$importdir is not a Git repo"

rm -rf "$importdir/"*
cp -a "$edgedir/Garmin/"* "$importdir/"
