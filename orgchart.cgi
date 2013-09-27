#!/usr/bin/env perl
use Data::Dumper;
use Net::LDAP;
use Template;

################################################################################
$ldap = Net::LDAP->new( 'example.org' );
$mesg = $ldap->bind( "cn=Scout Account,,ou=Users,dc=example,dc=org", password => $ENV{'AD_PASSWORD'});

$mesg->code && die $mesg->error;
$mesg = $ldap->search(base => "ou=Users,dc=exampl,dc=org", filter => "(manager=*)");
$mesg->code && die $mesg->error;

my $rows;
foreach $entry ($mesg->entries) {
    push(@{ $rows }, {
                       department => $entry->get_value( 'department' )||"no department",
                       displayName => $entry->get_value( 'displayName' )||"no display name",
                       manager => $entry->get_value( 'manager' )||"no manager",
                       description => $entry->get_value( 'description' )||"no description",
                       dn => $entry->dn||"no dn",
                     });
}

my $output_lines;

# owner won't be managed, so our search for "manager=*" will not bring them up...
push(@{ $output_lines }, qq([{v:'CN=John Smith,OU=Users,DC=example,DC=org', f:'John Smith<div style="color:red; font-style:italic">Owner</div>'}, '', 'John Smith'],) );

foreach my $row (@{ $rows }){
    push(@{ $output_lines }, qq([{v:'$row->{dn}', f:'$row->{displayName}<div style="color:green; font-style:italic">$row->{department}</div>'}, '$row->{manager}', '$row->{description}'],));
}

################################################################################
my $config = {
               INCLUDE_PATH => ['/var/www/templates'],
               INTERPOLATE  => 1,
               POST_CHOMP   => 1,
               EVAL_PERL    => 1,
             };

my $template = Template->new($config);

my $vars = { data_rows =>join("\n",@{ $output_lines}), };
my $input = 'orgchart.tpl';
my $output = '';

print "Content-type: text/html\n\n";
$template->process($input, $vars, \$output) || die $template->error();
print "$output\n";

